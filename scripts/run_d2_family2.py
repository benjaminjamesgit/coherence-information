#!/usr/bin/env python3
"""D2 Phase-2 driver (pre-registered 2026-06-24): SECOND-FAMILY replication (PF00026) + EDGE-M5.

Reuses the EXACT pinned method from scripts/pilot_d2_coupling.py / pilot_d2_bprime.py /
pilot_d2_b2.py, PARAMETERIZED by (acc, pdb, chain); adds the pre-registered EDGE-M5 AUROC.
Matrix-build recipe is bit-exact to the PF13354 pilot (verified: match-state columns by case,
gap-fraction < 0.5 on the np.random.default_rng(0).choice(n,2000,replace=False)-sorted subsample,
AA 'ACDEFGHIKLMNPQRSTVWY' -> 0..19, everything else -> 20). Outputs -> data/pfam/ (gitignored).
NOT committed (Phase-2 HARD STOP: no further commits). All HTTP via curl (no python TLS CA bundle).

PINS (unchanged): N=2000 seed 0; 80%-id reweighting; 21 states (gap=20); MIp APC; contacts
Cb-Cb<8A (Ca for Gly) |i-j|>=5; IQ-TREE LG+G4 -wsr per-site rates (VeryFastTree -lg guide tree);
HSExposureCB burial; q99=99th pct off-diag MIp; PageRank d=0.85; BLOSUM62 PDB->consensus mapping.
EDGE-M5: AUROC(MIp), AUROC(cons_i*cons_j), AUROC(burial_i*burial_j) over contact vs non-contact
pairs (|i-j|>=5), overall + long-range (|i-j|>=12), bootstrap CI (B=1000, resample pairs).
"""
import os, sys, gzip, json, subprocess, numpy as np
np.seterr(all="ignore")

PF="data/pfam"; AA="ACDEFGHIKLMNPQRSTVWY"; A2I={a:i for i,a in enumerate(AA)}
STATES=21; GAP=20; IDTHR=0.80; DCUT=8.0; SEP=5; LONG=12; DAMP=0.85; NBOOT=1000
THREE2ONE={"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G",
 "HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T",
 "TRP":"W","TYR":"Y","VAL":"V"}

# ---------- rank / spearman / partial (verbatim from the pilots) ----------
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

# ---------- matrix build (bit-exact to the PF13354 pilot) ----------
def parse_sto(path):
    names=[]; seqs=[]
    op=gzip.open if path.endswith(".gz") else open
    with op(path,"rt") as fh:
        for line in fh:
            line=line.rstrip("\n")
            if not line or line.startswith("#") or line.startswith("//"): continue
            p=line.split(None,1)
            if len(p)!=2: continue
            names.append(p[0]); seqs.append(p[1])
    return names,seqs

def build_matrix(acc):
    mp=f"{PF}/pilotS_{acc}_matrix.npy"; fp=f"{PF}/pilotS_{acc}.fasta"; jp=f"{PF}/pilot_{acc}_meta.json"
    if os.path.exists(mp) and os.path.exists(fp):
        meta=json.load(open(jp)); print(f"[build] {acc} matrix exists L={meta['L']}",flush=True); return meta
    aln=f"{PF}/aln_{acc}.sto.gz"
    if not os.path.exists(aln):
        url=f"https://www.ebi.ac.uk/interpro/api/entry/pfam/{acc}/?annotation=alignment:full"
        print(f"[build] downloading {acc} full alignment ...",flush=True)
        subprocess.run(["curl","-sS","-o",aln,url],check=True)
    names,seqs=parse_sto(aln)
    W=len(seqs[0]); assert all(len(s)==W for s in seqs),"ragged alignment"
    arr=np.array([list(s) for s in seqs]); n=arr.shape[0]
    print(f"[build] {acc}: {n} seqs x {W} cols",flush=True)
    match_cols=np.array([c for c in range(W)
                         if not(any(ch.islower() for ch in arr[:,c]) or ('.' in arr[:,c]))])
    idx=np.sort(np.random.default_rng(0).choice(n,2000,replace=False))
    sub=arr[idx]; gf=(sub[:,match_cols]=='-').mean(axis=0); kept=match_cols[gf<0.5]
    cols=sub[:,kept]
    M=np.full(cols.shape,GAP,dtype=np.int64)
    for i in range(cols.shape[0]):
        for j in range(cols.shape[1]):
            M[i,j]=A2I.get(cols[i,j],GAP)
    np.save(mp,M)
    with open(fp,"w") as fh:
        for r in range(M.shape[0]):
            fh.write(f">s{r}\n"+"".join(AA[v] if v<20 else "-" for v in M[r])+"\n")
    meta={"acc":acc,"N":int(M.shape[0]),"L":int(M.shape[1]),"seed":0,
          "kept_match_cols":[int(c) for c in kept]}
    json.dump(meta,open(jp,"w"))
    print(f"[build] {acc}: matrix {M.shape} saved",flush=True)
    return meta

def run_rates(acc):
    rp=f"{PF}/iq_{acc}.rate"
    if os.path.exists(rp): print(f"[rates] {acc} rate exists",flush=True); return rp
    fp=f"{PF}/pilotS_{acc}.fasta"; nwk=f"{PF}/pilotS_{acc}.nwk"
    if not os.path.exists(nwk):
        print(f"[rates] VeryFastTree {acc} ...",flush=True)
        with open(nwk,"w") as out:
            subprocess.run(["veryfasttree","-lg",fp],stdout=out,
                           stderr=open(f"{PF}/_vft_{acc}.log","w"),check=True)
    print(f"[rates] IQ-TREE LG+G4 -wsr {acc} ...",flush=True)
    subprocess.run(["iqtree3","-s",fp,"-te",nwk,"-m","LG+G4","-wsr","-nt","1",
                    "-pre",f"{PF}/iq_{acc}","-redo"],
                   stdout=open(f"{PF}/_iq_{acc}.log","w"),stderr=subprocess.STDOUT,check=True)
    return rp

def load_inv_tol(acc,L):
    sites={}
    for line in open(f"{PF}/iq_{acc}.rate"):
        if line.startswith("#") or line.lower().startswith("site"): continue
        p=line.split()
        if len(p)>=2:
            try: sites[int(p[0])]=float(p[1])
            except: pass
    return -np.array([sites.get(i+1,np.nan) for i in range(L)])

# ---------- coupling method (verbatim pins) ----------
def reweight(M):
    N,L=M.shape; match=np.zeros((N,N),dtype=np.float32)
    for s in range(STATES):
        B=(M==s).astype(np.float32); match+=B@B.T
    ident=match/L; neighbors=(ident>=IDTHR).sum(axis=1).astype(float)
    weights=1.0/neighbors; return weights,float(weights.sum())

def mip_matrix(M,weights):
    N,L=M.shape; wv=weights.astype(np.float64); Wsum=wv.sum()
    OH=np.zeros((N,L,STATES))
    for a in range(STATES): OH[:,:,a]=(M==a)
    fi=(wv[:,None,None]*OH).sum(axis=0)/Wsum
    OHflat=OH.reshape(N,L*STATES); MI=np.zeros((L,L))
    for i in range(L):
        Wi=(OH[:,i,:]*wv[:,None]); F=(Wi.T@OHflat).reshape(STATES,L,STATES)/Wsum
        fic=fi[i][:,None]
        for j in range(i+1,L):
            fij=F[:,j,:]; fjc=fi[j][None,:]; mask=fij>0
            MI[i,j]=MI[j,i]=float((fij[mask]*np.log(fij[mask]/(fic*fjc)[mask])).sum()) if mask.any() else 0.0
    iu=np.triu_indices(L,1); mi_i=MI.sum(axis=1)/(L-1); mi_all=MI[iu].mean()
    MIp=MI-np.outer(mi_i,mi_i)/mi_all; np.fill_diagonal(MIp,0.0)
    return MIp

def conservation(M):
    N,L=M.shape; ent=np.zeros(L)
    for j in range(L):
        nz=M[:,j][M[:,j]<GAP]
        if len(nz)==0: ent[j]=np.log2(20); continue
        c=np.bincount(nz,minlength=20).astype(float); p=c[c>0]/c.sum(); ent[j]=-(p*np.log2(p)).sum()
    return -ent

def map_pdb(M,pdb,chain):
    """Returns col2pdb, coords, chid, burial. Burial = HSExposureCB EXP_HSE_B_U computed on the
    SAME model whose chain residues are mapped (the pilot-B' method; avoids stale-residue xtra)."""
    N,L=M.shape; pdbf=f"{PF}/{pdb}.pdb"
    if not os.path.exists(pdbf):
        subprocess.run(["curl","-sS","-o",pdbf,f"https://files.rcsb.org/download/{pdb}.pdb"],check=True)
    from Bio.PDB import PDBParser
    from Bio.PDB.HSExposure import HSExposureCB
    model=PDBParser(QUIET=True).get_structure(pdb,pdbf)[0]
    HSExposureCB(model)  # populates res.xtra['EXP_HSE_B_U'] on this model's residues
    ch=model[chain] if chain in model else list(model)[0]
    pres=[]
    for res in ch:
        if res.id[0]!=" ": continue
        nm=res.resname.upper()
        if nm not in THREE2ONE: continue
        atom="CA" if nm=="GLY" else ("CB" if "CB" in res else "CA")
        if atom not in res: continue
        pres.append((THREE2ONE[nm],res[atom].coord,res))
    pdb_seq="".join(r[0] for r in pres); coords=np.array([r[1] for r in pres])
    cons_seq="".join(AA[np.bincount(M[:,j][M[:,j]<GAP],minlength=20).argmax()] if (M[:,j]<GAP).any() else "A" for j in range(L))
    from Bio.Align import PairwiseAligner,substitution_matrices
    al=PairwiseAligner(); al.substitution_matrix=substitution_matrices.load("BLOSUM62")
    al.open_gap_score=-11; al.extend_gap_score=-1; al.mode="global"
    aln=al.align(cons_seq,pdb_seq)[0]; idx=aln.indices
    col2pdb={int(idx[0,k]):int(idx[1,k]) for k in range(idx.shape[1]) if idx[0,k]>=0 and idx[1,k]>=0}
    burial=np.full(L,np.nan)
    for col,k in col2pdb.items():
        burial[col]=pres[k][2].xtra.get("EXP_HSE_B_U",np.nan)
    return col2pdb,coords,chid_of(ch),burial

def chid_of(ch): return ch.id

def contacts(col2pdb,coords,L):
    mapped=sorted(col2pdb); cpair=set(); cdeg=np.zeros(L)
    for x in range(len(mapped)):
        for y in range(x+1,len(mapped)):
            i,j=mapped[x],mapped[y]
            if abs(i-j)<SEP: continue
            if np.linalg.norm(coords[col2pdb[i]]-coords[col2pdb[j]])<DCUT:
                cpair.add((i,j)); cdeg[i]+=1; cdeg[j]+=1
    return mapped,cpair,cdeg

# ---------- B' / B2 node projections ----------
def bprime(MIp,L):
    MZ=MIp.copy(); np.fill_diagonal(MZ,0.0)
    s_max=MZ.max(axis=1)
    s_top5=np.sort(MZ,axis=1)[:,-5:].mean(axis=1)
    q99=np.percentile(MIp[np.triu_indices(L,1)],99); s_cnt=(MZ>q99).sum(axis=1).astype(float)
    return {"s_max":s_max,"s_top5":s_top5,"s_cnt":s_cnt},q99

def b2proj(MIp,mapped,L):
    W=np.maximum(MIp,0.0); np.fill_diagonal(W,0.0)
    val,vec=np.linalg.eigh(W); v=vec[:,-1]; v=v*np.sign(v.sum() if v.sum()!=0 else 1.0); g_eig=np.abs(v)
    rs=W.sum(axis=1); S=np.zeros_like(W); nz=rs>0; S[nz]=W[nz]/rs[nz,None]; S[~nz]=1.0/L
    pr=np.full(L,1.0/L)
    for _ in range(1000):
        nxt=DAMP*(S.T@pr)+(1-DAMP)/L
        if np.abs(nxt-pr).sum()<1e-12: pr=nxt; break
        pr=nxt
    mp=mapped; elig=[(mp[x],mp[y]) for x in range(len(mp)) for y in range(x+1,len(mp)) if abs(mp[x]-mp[y])>=SEP]
    topL=sorted(elig,key=lambda p:-MIp[p[0],p[1]])[:len(mp)]
    g_topL=np.zeros(L)
    for i,j in topL: g_topL[i]+=1; g_topL[j]+=1
    return {"g_eig":g_eig,"g_pr":pr,"g_topL":g_topL}

# ---------- AUROC + edge-M5 ----------
def auroc2(scores,labels):
    scores=np.asarray(scores,float); labels=np.asarray(labels,bool)
    m=~np.isnan(scores); scores,labels=scores[m],labels[m]
    npos=int(labels.sum()); nneg=int((~labels).sum())
    if npos==0 or nneg==0: return float("nan")
    r=rank(scores)  # average ranks, 0-based
    sum_pos=r[labels].sum()+npos  # convert to 1-based rank sum
    U=sum_pos-npos*(npos+1)/2.0
    return float(U/(npos*nneg))

def edge_m5(MIp,cons,bur,cpair,mapped,tag):
    # common support: mapped pairs with both endpoints burial-defined
    burdef=[c for c in mapped if np.isfinite(bur[c])]
    def pairset(cols,longonly):
        out=[]
        for x in range(len(cols)):
            for y in range(x+1,len(cols)):
                i,j=cols[x],cols[y]; d=abs(i-j)
                if d<SEP: continue
                if longonly and d<LONG: continue
                out.append((i,j))
        return out
    res={}
    rng=np.random.default_rng(0)
    for split,longonly in (("overall",False),("long",True)):
        pairs=pairset(burdef,longonly)
        if not pairs: res[split]=None; continue
        lab=np.array([(p in cpair) for p in pairs])
        sM=np.array([MIp[p] for p in pairs])
        sC=np.array([cons[p[0]]*cons[p[1]] for p in pairs])
        sB=np.array([bur[p[0]]*bur[p[1]] for p in pairs])
        aM,aC,aB=auroc2(sM,lab),auroc2(sC,lab),auroc2(sB,lab)
        # bootstrap CI on MIp-AUROC (resample pairs)
        idx=np.arange(len(pairs)); boots=[]
        for _ in range(NBOOT):
            bi=rng.integers(0,len(pairs),len(pairs))
            boots.append(auroc2(sM[bi],lab[bi]))
        lo,hi=np.nanpercentile(boots,[2.5,97.5])
        res[split]={"n_pairs":len(pairs),"n_contact":int(lab.sum()),
                    "AUROC_MIp":aM,"AUROC_consprod":aC,"AUROC_burialprod":aB,
                    "MIp_CI":[float(lo),float(hi)]}
        print(f"  [edge-M5 {tag} {split}] pairs={len(pairs)} contacts={int(lab.sum())} | "
              f"AUROC MIp={aM:.3f} (CI {lo:.3f},{hi:.3f}) cons2={aC:.3f} bur2={aB:.3f}",flush=True)
    passed = (res["overall"] and res["long"] and
              res["overall"]["AUROC_MIp"]>res["overall"]["AUROC_consprod"] and
              res["overall"]["AUROC_MIp"]>res["overall"]["AUROC_burialprod"] and
              res["overall"]["MIp_CI"][0]>0.5)
    res["EDGE_M5_overall_pass"]=bool(passed)
    return res

def margin_ci(g,cdeg,bur,ref,mm):
    """bootstrap CI of partial(g,cdeg|bur) - partial(ref,cdeg|bur) over positions."""
    idx=np.where(mm)[0]; rng=np.random.default_rng(0); boots=[]
    gp0=partial(g[idx],cdeg[idx],bur[idx]); rp0=partial(ref[idx],cdeg[idx],bur[idx])
    for _ in range(NBOOT):
        bi=rng.integers(0,len(idx),len(idx)); s=idx[bi]
        gp=partial(g[s],cdeg[s],bur[s]); rp=partial(ref[s],cdeg[s],bur[s]); boots.append(gp-rp)
    lo,hi=np.nanpercentile(boots,[2.5,97.5])
    return gp0-rp0,float(lo),float(hi)

# ---------- family run ----------
def run_family(acc,pdb,chain):
    print(f"\n========== FAMILY {acc}  PDB {pdb}:{chain} ==========",flush=True)
    meta=build_matrix(acc); M=np.load(f"{PF}/pilotS_{acc}_matrix.npy"); N,L=M.shape
    npzp=f"{PF}/pilot_coupling_{acc}.npz"
    if os.path.exists(npzp):
        d=np.load(npzp); MIp=d["MIp"]; cons=d["conservation"]; inv_tol=d["inv_tol"]; Meff=float(d["Meff"])
        print(f"[reuse] MIp/cons/inv_tol from {npzp}; Meff={Meff:.1f}",flush=True)
    else:
        run_rates(acc); inv_tol=load_inv_tol(acc,L)
        w,Meff=reweight(M); print(f"Meff={Meff:.1f}",flush=True)
        MIp=mip_matrix(M,w); cons=conservation(M)
    col2pdb,coords,chid,bur=map_pdb(M,pdb,chain)
    mapped,cpair,cdeg=contacts(col2pdb,coords,L)
    cov=len(mapped); print(f"mapping coverage {cov}/{L} ({100*cov/L:.0f}%); contacts={len(cpair)}",flush=True)
    # check A
    elig=[(mapped[x],mapped[y]) for x in range(len(mapped)) for y in range(x+1,len(mapped)) if abs(mapped[x]-mapped[y])>=SEP]
    Ltop=len(mapped); base=len(cpair)/len(elig) if elig else float("nan")
    precM=np.mean([1.0 if p in cpair else 0.0 for p in sorted(elig,key=lambda p:-MIp[p])[:Ltop]])
    precC=np.mean([1.0 if p in cpair else 0.0 for p in sorted(elig,key=lambda p:-(cons[p[0]]*cons[p[1]]))[:Ltop]])
    print(f"[A] top-L MIp precision={precM:.3f} cons-prod={precC:.3f} base={base:.3f}",flush=True)
    # B'/B2 evaluation positions = mapped & burial-defined
    mm=np.zeros(L,bool)
    for c in mapped:
        if np.isfinite(bur[c]): mm[c]=True
    cons_par=partial(cons[mm],cdeg[mm],bur[mm])
    inv_par=partial(inv_tol[mm],cdeg[mm],bur[mm])
    print(f"[refs] conservation partial|burial={cons_par:+.3f}  phylo-invtol partial|burial={inv_par:+.3f}  (positions={mm.sum()})",flush=True)
    aggs,q99=bprime(MIp,L); projs=b2proj(MIp,mapped,L)
    bp={}
    for nm,g in aggs.items():
        pa=partial(g[mm],cdeg[mm],bur[mm]); bp[nm]={"partial":pa,"beats_cons":bool(pa>0 and pa>cons_par)}
        print(f"  B' {nm:6s} partial|burial={pa:+.3f} beats_cons={pa>0 and pa>cons_par}",flush=True)
    b2={}
    for nm,g in projs.items():
        pa=partial(g[mm],cdeg[mm],bur[mm]); b2[nm]={"partial":pa,"beats_cons":bool(pa>0 and pa>cons_par)}
        print(f"  B2 {nm:6s} partial|burial={pa:+.3f} beats_cons={pa>0 and pa>cons_par}",flush=True)
    # hardened: g_pr margin vs BOTH refs + CI
    d_ent,lo_e,hi_e=margin_ci(projs["g_pr"],cdeg,bur,cons,mm)
    d_phy,lo_p,hi_p=margin_ci(projs["g_pr"],cdeg,bur,inv_tol,mm)
    print(f"  [hardened g_pr] margin vs entropy-cons={d_ent:+.3f} CI[{lo_e:+.3f},{hi_e:+.3f}] | "
          f"vs phylo-invtol={d_phy:+.3f} CI[{lo_p:+.3f},{hi_p:+.3f}]",flush=True)
    robust=bool(d_phy>0 and lo_p>0)
    print(f"  ROBUST node pass (g_pr beats phylo-cons, margin-CI excludes 0)? {robust}",flush=True)
    em=edge_m5(MIp,cons,bur,cpair,mapped,acc)
    out={"acc":acc,"pdb":pdb,"chain":chid,"N":N,"L":L,"Meff":Meff,"coverage":cov,
         "A":{"precM":precM,"precC":precC,"base":base},
         "refs":{"cons_partial":cons_par,"invtol_partial":inv_par,"positions":int(mm.sum())},
         "Bprime":bp,"B2":b2,
         "hardened_gpr":{"margin_vs_entropy":d_ent,"CI_entropy":[lo_e,hi_e],
                         "margin_vs_phylo":d_phy,"CI_phylo":[lo_p,hi_p],"robust":robust},
         "edge_m5":em}
    np.savez(f"{PF}/pilot_coupling_{acc}.npz",MIp=MIp,contact_degree=cdeg,conservation=cons,
             inv_tol=inv_tol,mapped=np.array(mapped),burial=bur,Meff=Meff,coverage=cov)
    json.dump(out,open(f"{PF}/pilot_family2_{acc}.json","w"),indent=2,default=float)
    print(f"[saved] {PF}/pilot_family2_{acc}.json",flush=True)
    return out

def edge_m5_pf13354():
    print("\n========== PF13354 EDGE-M5 FOLD-IN ==========",flush=True)
    d=np.load(f"{PF}/pilot_coupling_PF13354.npz"); MIp=d["MIp"]; cons=d["conservation"]
    mapped=sorted(int(x) for x in d["mapped"]); L=MIp.shape[0]
    bur=np.load(f"{PF}/pilot_b2_PF13354.npz")["burial"]
    M=np.load(f"{PF}/pilotS_PF13354_matrix.npy")
    col2pdb,coords,chid,_b=map_pdb(M,"1djc","A")
    _,cpair,_=contacts(col2pdb,coords,L)
    em=edge_m5(MIp,cons,bur,cpair,mapped,"PF13354")
    json.dump(em,open(f"{PF}/pilot_edge_m5_PF13354.json","w"),indent=2,default=float)
    print(f"[saved] {PF}/pilot_edge_m5_PF13354.json",flush=True)
    return em

if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "all"
    if mode=="build":
        build_matrix("PF00026")
    elif mode=="rates":
        run_rates("PF00026")
    elif mode=="pf13354":
        edge_m5_pf13354()
    else:
        run_family("PF00026","4y9w","A"); edge_m5_pf13354()
