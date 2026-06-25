#!/usr/bin/env python3
"""D2 RELATIONAL BUILD step 5 PHASE 1 -- deterministic clean-tree THIRD-family selection.

OUTCOME-INDEPENDENT gates (pre-computation). From candidate_pool.tsv, lowest Pfam accession with
catalytic=YES, oversized=False, depth 1500+, NOT PF13354/PF00026, AND:
  (g1) >= 150 match columns under the pinned build_matrix recipe;
  (g2) a clean single-domain PDB <= 2.5 A x-ray (InterPro: ONLY this Pfam family on the whole PDB,
       and a single domain fragment on the chosen chain -- no tandem copies);
  (g3) BALANCED tree (the fix for PF00026's caterpillar degeneracy): the K=8 greedy cut of the
       midpoint-rooted tree gives K_eff >= 6 subclades with NO subclade > 40% of the 2000 seqs.
       Screened on the fast VeryFastTree tree; CONFIRMED on the pinned IQ tree for the winner.
Tree balance is a property of the BUILT tree (data-quality), NOT an R1 result -> selecting on it is
outcome-independent. Records every skip + reason; stops at the first full pass; writes the lock to
data/pfam/third_family_lock.json. Reuses run_d2_family2.build_matrix/run_rates (pinned recipe).
HTTP via curl. NOT committed (data/ gitignored).
"""
import os, sys, csv, json, re, subprocess
import numpy as np
from Bio import Phylo

sys.path.insert(0, "scripts")
from run_d2_family2 import build_matrix, run_rates, PF

K = 8
MIN_CLADE = 25
BAL_KEFF = 6
BAL_MAXFRAC = 0.40
RES_MAX = 2.5
MIN_COLS = 150
MAX_EVAL = 40
EXCLUDE = {"PF13354", "PF00026"}
IPRO = "https://www.ebi.ac.uk/interpro/api"


def curl_json(url, tries=3):
    last = None
    for _ in range(tries):
        out = subprocess.run(["curl", "-sS", url], capture_output=True, text=True)
        try:
            return json.loads(out.stdout)
        except Exception as e:
            last = e
    raise RuntimeError(f"curl_json failed {url}: {last}")


def leaf_row(name):
    return int(re.sub(r"^[A-Za-z]+", "", name))


def shortlist():
    rows = list(csv.DictReader(open(f"{PF}/candidate_pool.tsv"), delimiter="\t"))
    sl = [r for r in rows if r["catalytic"] == "YES" and r["oversized"] == "False"
          and r["depth"] == "1500+" and r["acc"] not in EXCLUDE]
    sl.sort(key=lambda r: r["acc"])
    return sl


TVFT = 300  # VeryFastTree completes in ~30s on a healthy 2000-taxa alignment; a >300s run signals a
            # pathological alignment incompatible with the pinned tree pipeline -> deterministic skip.


def run_vft(acc):
    nwk = f"{PF}/pilotS_{acc}.nwk"
    fp = f"{PF}/pilotS_{acc}.fasta"
    if os.path.exists(nwk) and os.path.getsize(nwk) > 0:
        return nwk
    try:
        with open(nwk, "w") as out:
            subprocess.run(["veryfasttree", "-lg", fp], stdout=out,
                           stderr=open(f"{PF}/_vft_{acc}.log", "w"), check=True, timeout=TVFT)
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        if os.path.exists(nwk):
            os.remove(nwk)
        raise RuntimeError(f"VFT tree build failed/timed out (>{TVFT}s; pinned-pipeline-incompatible / "
                           f"pathological alignment): {type(e).__name__}")
    return nwk


def tree_balance(treepath):
    """K=8 greedy top-down cut of the midpoint-rooted tree (same logic as r1_edge.cut_into_subclades);
    subclades < MIN_CLADE merged into nearest by tree distance. Returns (K_eff, sorted_sizes, max_frac)."""
    tree = Phylo.read(treepath, "newick")
    tree.root_at_midpoint()
    groups = [tree.root]
    while len(groups) < K:
        cand = [g for g in groups if len(g.clades) >= 2]
        if not cand:
            break
        cand.sort(key=lambda g: (-len(g.get_terminals()),
                                 min(leaf_row(t.name) for t in g.get_terminals())))
        g = cand[0]
        groups.remove(g)
        groups.extend(g.clades)
    rows = [[leaf_row(t.name) for t in g.get_terminals()] for g in groups]
    big = [(g, r) for g, r in zip(groups, rows) if len(r) >= MIN_CLADE]
    small = [(g, r) for g, r in zip(groups, rows) if len(r) < MIN_CLADE]
    keep_g = [g for g, _ in big]
    keep_rows = [list(r) for _, r in big]
    for gs, rs in small:
        t = int(np.argmin([tree.distance(gs, gb) for gb in keep_g]))
        keep_rows[t] += rs
    sizes = sorted(len(r) for r in keep_rows)
    return len(keep_rows), sizes, max(sizes) / sum(sizes)


def resolve_pdb(acc):
    """First (best-resolution) clean single-domain x-ray PDB <= RES_MAX: only this Pfam on the whole
    structure, single domain fragment on the chosen chain. Returns (pdb_lower, chain, resolution) or None."""
    url = f"{IPRO}/structure/pdb/entry/pfam/{acc}/?page_size=200"
    cands = []
    while url:
        d = curl_json(url)
        for r in d["results"]:
            m = r["metadata"]
            if m.get("experiment_type") != "x-ray":
                continue
            res = m.get("resolution")
            if res is None or res > RES_MAX:
                continue
            for e in r["entries"]:
                if e["accession"].upper() != acc:
                    continue
                nfrag = sum(len(l["fragments"]) for l in e.get("entry_protein_locations", []))
                ch = e.get("chain")
                if nfrag == 1 and ch:
                    cands.append((float(res), m["accession"].lower(), ch))
        url = d.get("next")
    cands.sort(key=lambda c: (c[0], c[1], c[2]))
    for res, pdb, ch in cands:
        dd = curl_json(f"{IPRO}/entry/pfam/structure/pdb/{pdb}/")
        accs = sorted({x["metadata"]["accession"].upper() for x in dd["results"]})
        if dd.get("count") == 1 and accs == [acc]:
            return pdb, ch, res
    return None


def main():
    sl = shortlist()
    print(f"[select] shortlist {len(sl)} (catalytic/not-oversized/1500+/not-PF13354,PF00026)", flush=True)
    skips = []
    for n, r in enumerate(sl):
        if n >= MAX_EVAL:
            print(f"[select] hit MAX_EVAL={MAX_EVAL} with no pass; skips so far:")
            for a, why in skips:
                print(f"   skip {a}: {why}")
            return None
        acc = r["acc"]
        try:
            meta = build_matrix(acc)
            L = meta["L"]
            if L < MIN_COLS:
                skips.append((acc, f"g1 cols={L}<{MIN_COLS}"))
                print(f"[skip] {acc}: cols={L}<{MIN_COLS}", flush=True)
                continue
            pdb = resolve_pdb(acc)
            if pdb is None:
                skips.append((acc, f"g2 no clean single-domain x-ray PDB <= {RES_MAX}A (cols={L})"))
                print(f"[skip] {acc}: no clean single-domain PDB <= {RES_MAX}A (cols={L})", flush=True)
                continue
            pdb_id, chain, res = pdb
            run_vft(acc)
            keff, sizes, maxfrac = tree_balance(f"{PF}/pilotS_{acc}.nwk")
            if keff < BAL_KEFF or maxfrac > BAL_MAXFRAC:
                skips.append((acc, f"g3 VFT-unbalanced K_eff={keff} maxfrac={maxfrac:.3f} "
                                   f"(cols={L}, pdb={pdb_id}:{chain}@{res}A, sizes={sizes})"))
                print(f"[skip] {acc}: VFT-unbalanced K_eff={keff} maxfrac={maxfrac:.3f} sizes={sizes}", flush=True)
                continue
            print(f"[winner?] {acc}: cols={L} pdb={pdb_id}:{chain}@{res}A VFT K_eff={keff} maxfrac={maxfrac:.3f}; "
                  f"building IQ tree to CONFIRM balance ...", flush=True)
            run_rates(acc)
            keff_iq, sizes_iq, maxfrac_iq = tree_balance(f"{PF}/iq_{acc}.treefile")
            if keff_iq < BAL_KEFF or maxfrac_iq > BAL_MAXFRAC:
                skips.append((acc, f"g3 VFT-balanced but IQ-unbalanced K_eff={keff_iq} maxfrac={maxfrac_iq:.3f} "
                                   f"sizes={sizes_iq}"))
                print(f"[skip] {acc}: IQ-unbalanced K_eff={keff_iq} maxfrac={maxfrac_iq:.3f} sizes={sizes_iq}", flush=True)
                continue
            lock = {"acc": acc, "id": r["id"], "fold": r["fold"], "pdb": pdb_id, "chain": chain,
                    "resolution": res, "L": L,
                    "vft_balance": {"K_eff": keff, "max_frac": maxfrac, "sizes": sizes},
                    "iq_balance": {"K_eff": keff_iq, "max_frac": maxfrac_iq, "sizes": sizes_iq},
                    "skips": [{"acc": a, "reason": why} for a, why in skips]}
            json.dump(lock, open(f"{PF}/third_family_lock.json", "w"), indent=2, default=float)
            print(f"\n[LOCKED] {acc} ({r['id']}) pdb={pdb_id}:{chain} res={res}A cols={L} "
                  f"IQ K_eff={keff_iq} maxfrac={maxfrac_iq:.3f} sizes={sizes_iq}", flush=True)
            print(f"[select] skips before winner: {[(a, w) for a, w in skips]}", flush=True)
            return lock
        except Exception as ex:
            skips.append((acc, f"ERROR {type(ex).__name__}: {ex}"))
            print(f"[skip] {acc}: ERROR {type(ex).__name__}: {ex}", flush=True)
            continue
    print("[select] exhausted shortlist with no pass")
    return None


if __name__ == "__main__":
    main()
