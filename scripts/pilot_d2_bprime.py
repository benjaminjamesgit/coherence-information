#!/usr/bin/env python3
"""D2 beta-line check B' (pre-registered 2026-06-24, pre_registration.md): the edge->node
projection of the coevolution signal, BURIAL-CONTROLLED. REUSES the existing MIp/.npz
(does NOT recompute MIp). Standalone; outputs -> data/pfam/ (gitignored).

PINS (from the B' pre-registration):
  node aggregations from MIp: s_max(i)=max_j MIp(i,j); s_top5(i)=mean top-5 MIp(i,j);
    s_cnt(i)=#{j: MIp(i,j) > q99}, q99 = 99th pct of off-diagonal MIp.
  burial proxy = Cb half-sphere exposure HSExposureCB (EXP_HSE_B_U) on 1djc:A, no external binary.
  T1 = raw Spearman(s_agg, contact_degree); T2 = first-order partial Spearman(., contact_degree | burial).
  B'-PASS iff at least one aggregation's partial(s_agg, contact_degree | burial) is BOTH > 0
    AND > conservation's partial(conservation, contact_degree | burial).
"""
import numpy as np
from Bio.PDB import PDBParser
from Bio.PDB.HSExposure import HSExposureCB

NPZ="data/pfam/pilot_coupling_PF13354.npz"; MAT="data/pfam/pilotS_PF13354_matrix.npy"; PDBF="data/pfam/1djc.pdb"
CHAIN="A"; GAP=20; AA="ACDEFGHIKLMNPQRSTVWY"
THREE2ONE={"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G",
 "HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T",
 "TRP":"W","TYR":"Y","VAL":"V"}

def rank(a):
    a=np.asarray(a,float); o=a.argsort(kind="mergesort"); r=np.empty(len(a)); r[o]=np.arange(len(a))
    s=a[o]; i=0
    while i<len(s):
        j=i
        while j+1<len(s) and s[j+1]==s[i]: j+=1
        if j>i: r[o[i:j+1]]=(i+j)/2.0
        i=j+1
    return r
def spear(x,y):
    x=np.asarray(x,float); y=np.asarray(y,float); m=~(np.isnan(x)|np.isnan(y)); x,y=x[m],y[m]
    if len(x)<3 or np.std(x)==0 or np.std(y)==0: return float("nan")
    return float(np.corrcoef(rank(x),rank(y))[0,1])
def partial(x,y,z):
    rxy=spear(x,y); rxz=spear(x,z); ryz=spear(y,z)
    den=np.sqrt((1-rxz**2)*(1-ryz**2))
    return float((rxy-rxz*ryz)/den) if den>0 else float("nan")

def main():
    d=np.load(NPZ)
    MIp=d["MIp"]; contact_degree=d["contact_degree"]; conservation=d["conservation"]
    mapped_saved=set(int(x) for x in d["mapped"]); L=MIp.shape[0]
    B_orig=float(d["B_s"])

    # --- node aggregations (off-diagonal) ---
    MZ=MIp.copy(); np.fill_diagonal(MZ,-np.inf)
    s_max=MZ.max(axis=1)
    s_top5=np.sort(MZ,axis=1)[:,-5:].mean(axis=1)
    q99=np.percentile(MIp[np.triu_indices(L,1)],99)
    s_cnt=(MZ>q99).sum(axis=1).astype(float)

    # --- re-derive col2pdb (same consensus-align method) + HSExposureCB burial ---
    M=np.load(MAT)
    model=PDBParser(QUIET=True).get_structure("1djc",PDBF)[0]
    HSExposureCB(model)  # populates res.xtra['EXP_HSE_B_U']
    ch=model[CHAIN] if CHAIN in model else list(model)[0]
    pres=[]  # (1-letter, residue)
    for res in ch:
        if res.id[0]!=" ": continue
        nm=res.resname.upper()
        if nm not in THREE2ONE: continue
        atom="CA" if nm=="GLY" else ("CB" if "CB" in res else "CA")
        if atom not in res: continue
        pres.append((THREE2ONE[nm],res))
    pdb_seq="".join(p[0] for p in pres)
    cons_seq="".join(AA[np.bincount(M[:,j][M[:,j]<GAP],minlength=20).argmax()] if (M[:,j]<GAP).any() else "A" for j in range(L))
    from Bio.Align import PairwiseAligner, substitution_matrices
    al=PairwiseAligner(); al.substitution_matrix=substitution_matrices.load("BLOSUM62")
    al.open_gap_score=-11; al.extend_gap_score=-1; al.mode="global"
    idx=al.align(cons_seq,pdb_seq)[0].indices
    col2pdb={int(idx[0,k]):int(idx[1,k]) for k in range(idx.shape[1]) if idx[0,k]>=0 and idx[1,k]>=0}
    assert set(col2pdb)==mapped_saved, f"mapping mismatch vs .npz: {len(set(col2pdb))} vs {len(mapped_saved)}"
    burial=np.full(L,np.nan)
    for col,k in col2pdb.items():
        burial[col]=pres[k][1].xtra.get("EXP_HSE_B_U",np.nan)
    nb=np.isfinite(burial).sum()
    print(f"burial (HSE_B_U) defined on {nb} of {len(col2pdb)} mapped columns (Gly/missing-Cb dropped); q99(MIp)={q99:.4f}", flush=True)

    # --- evaluate over mapped+burial-defined positions ---
    mm=np.zeros(L,bool)
    for c in col2pdb:
        if np.isfinite(burial[c]): mm[c]=True
    cons_partial=partial(conservation[mm],contact_degree[mm],burial[mm])
    cons_raw=spear(conservation[mm],contact_degree[mm])
    print(f"\n===== B' (PF13354) =====  positions used = {mm.sum()}")
    print(f"original B (Spearman s_sum, contact_degree, no burial control) = {B_orig:+.3f}")
    print(f"conservation: raw Spearman(.,contact_degree)={cons_raw:+.3f}  partial(.|burial)={cons_partial:+.3f}")
    print(f"context: Spearman(contact_degree, burial)={spear(contact_degree[mm],burial[mm]):+.3f}  Spearman(conservation, burial)={spear(conservation[mm],burial[mm]):+.3f}\n")
    aggs={"s_max":s_max,"s_top5":s_top5,"s_cnt":s_cnt}
    results={}
    passers=[]
    for nmn,ag in aggs.items():
        raw=spear(ag[mm],contact_degree[mm]); pa=partial(ag[mm],contact_degree[mm],burial[mm])
        beats = (pa>0) and (pa>cons_partial)
        if beats: passers.append(nmn)
        results[nmn]={"raw":raw,"partial":pa,"beats_cons":bool(beats)}
        print(f"  {nmn:7s}: raw Spearman(.,contact_degree)={raw:+.3f}  partial(.|burial)={pa:+.3f}  >0 & >cons? {beats}")
    verdict = "B'-PASS" if passers else "B'-FAIL"
    print(f"\nVERDICT: {verdict}  (aggregations beating conservation on burial-controlled partial: {passers or 'NONE'})")
    print(f"DECISION: {'beta buildable at per-position granularity -> joint-proxy design (separate)' if passers else 'edge->node loss real -> ESCALATE the Sec 6.2 per-position-w question'}")
    np.savez("data/pfam/pilot_bprime_PF13354.npz", s_max=s_max, s_top5=s_top5, s_cnt=s_cnt,
             burial=burial, cons_partial=cons_partial, results=str(results), verdict=verdict)
    print("saved data/pfam/pilot_bprime_PF13354.npz", flush=True)

if __name__=="__main__":
    main()
