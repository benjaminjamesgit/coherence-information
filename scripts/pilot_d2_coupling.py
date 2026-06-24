#!/usr/bin/env python3
"""D2 beta-direction premise check: is there a SEPARABLE cross-position COUPLING
(coevolution) signal in PF13354, distinct from per-site conservation?

Standalone measurement. REUSES pinned artifacts only (matrix, IQ-TREE rates, PDB 1djc).
Does NOT touch the KxA grid, the proxies, or pre_registration.md. Contacts + MIp enter as
COMPARISON-COMPRESSIONS (Meta-Coherence Sec 6.4 idiom), NOT a ground-truth oracle: the probe
asks "is there a separable coupling signal to induce w toward", not "does w match truth".
Outputs -> data/pfam/ (gitignored).

PINS: PF13354, N=2000 (seed 0), 248 match columns, alphabet 21 (gap=20);
PDB 1djc chain A; contact = Cb-Cb (Ca for Gly) < 8.0 A, |i-j| >= 5;
reweighting identity threshold 0.80 over all 248 columns (gaps count as matches);
MIp over 21 states (gap included), APC-corrected; column entropy GAP-EXCLUDED (20-AA renormalized).
"""
import os, subprocess, numpy as np

MAT="data/pfam/pilotS_PF13354_matrix.npy"; RATE="data/pfam/iq_PF13354.rate"; PDBF="data/pfam/1djc.pdb"
PDB_ID="1djc"; CHAIN="A"; DCUT=8.0; SEP=5; IDTHR=0.80; STATES=21; GAP=20
AA="ACDEFGHIKLMNPQRSTVWY"
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

def main():
    M=np.load(MAT); N,L=M.shape; print(f"matrix {N} x {L}", flush=True)
    sites={}
    for line in open(RATE):
        if line.startswith("#") or line.lower().startswith("site"): continue
        p=line.split()
        if len(p)>=2:
            try: sites[int(p[0])]=float(p[1])
            except: pass
    inv_tol=-np.array([sites.get(i+1,np.nan) for i in range(L)])

    # STEP 1: sequence reweighting (identity >= 0.80 over all L columns, gaps count) ---
    match=np.zeros((N,N),dtype=np.float32)
    for s in range(STATES):
        B=(M==s).astype(np.float32); match += B @ B.T
    ident=match/L; neighbors=(ident>=IDTHR).sum(axis=1).astype(float)
    weights=1.0/neighbors; Meff=float(weights.sum())
    print(f"Meff = {Meff:.1f} (mean neighbors {neighbors.mean():.1f})", flush=True)

    # STEP 2: reweighted MIp ---
    wv=weights.astype(np.float64); Wsum=wv.sum()
    OH=np.zeros((N,L,STATES))
    for a in range(STATES): OH[:,:,a]=(M==a)
    fi=(wv[:,None,None]*OH).sum(axis=0)/Wsum   # L x STATES
    OHflat=OH.reshape(N,L*STATES)
    MI=np.zeros((L,L))
    for i in range(L):
        Wi=(OH[:,i,:]*wv[:,None])            # N x STATES (weighted)
        F=(Wi.T @ OHflat).reshape(STATES,L,STATES)/Wsum   # f_ij(a,b) for all j
        fic=fi[i][:,None]
        for j in range(i+1,L):
            fij=F[:,:,:][:,j,:]; fjc=fi[j][None,:]; mask=fij>0
            MI[i,j]=MI[j,i]=float((fij[mask]*np.log(fij[mask]/(fic*fjc)[mask])).sum()) if mask.any() else 0.0
    iu=np.triu_indices(L,1)
    mi_i=MI.sum(axis=1)/(L-1); mi_all=MI[iu].mean()
    MIp=MI-np.outer(mi_i,mi_i)/mi_all; np.fill_diagonal(MIp,0.0)
    s_i=MIp.sum(axis=1)
    print(f"raw-MI mean={MI[iu].mean():.4f}  MIp mean={MIp[iu].mean():.4f}", flush=True)

    # STEP 4: conservation (entropy GAP-EXCLUDED, 20-AA renormalized) ---
    ent=np.zeros(L)
    for j in range(L):
        nz=M[:,j][M[:,j]<GAP]
        if len(nz)==0: ent[j]=np.log2(20); continue
        c=np.bincount(nz,minlength=20).astype(float); p=c[c>0]/c.sum(); ent[j]=-(p*np.log2(p)).sum()
    conservation=-ent

    # STEP 3: contacts from 1djc ---
    if not os.path.exists(PDBF):
        subprocess.run(["curl","-sS","-o",PDBF,f"https://files.rcsb.org/download/{PDB_ID}.pdb"],check=True)
    from Bio.PDB import PDBParser
    model=PDBParser(QUIET=True).get_structure(PDB_ID,PDBF)[0]
    ch=model[CHAIN] if CHAIN in model else list(model)[0]
    pres=[]
    for res in ch:
        if res.id[0]!=" ": continue
        nm=res.resname.upper()
        if nm not in THREE2ONE: continue
        atom="CA" if nm=="GLY" else ("CB" if "CB" in res else "CA")
        if atom not in res: continue
        pres.append((THREE2ONE[nm], res[atom].coord))
    pdb_seq="".join(r[0] for r in pres); coords=np.array([r[1] for r in pres])
    cons_seq="".join(AA[np.bincount(M[:,j][M[:,j]<GAP],minlength=20).argmax()] if (M[:,j]<GAP).any() else "A" for j in range(L))
    from Bio.Align import PairwiseAligner, substitution_matrices
    al=PairwiseAligner(); al.substitution_matrix=substitution_matrices.load("BLOSUM62")
    al.open_gap_score=-11; al.extend_gap_score=-1; al.mode="global"
    aln=al.align(cons_seq,pdb_seq)[0]; idx=aln.indices
    col2pdb={int(idx[0,k]):int(idx[1,k]) for k in range(idx.shape[1]) if idx[0,k]>=0 and idx[1,k]>=0}
    mapped=sorted(col2pdb); coverage=len(mapped)
    print(f"PDB {PDB_ID}:{ch.id} residues={len(pres)} | mapping coverage {coverage}/{L}", flush=True)
    contact_pair=set(); contact_degree=np.zeros(L)
    for x in range(len(mapped)):
        for y in range(x+1,len(mapped)):
            i,j=mapped[x],mapped[y]
            if abs(i-j)<SEP: continue
            if np.linalg.norm(coords[col2pdb[i]]-coords[col2pdb[j]])<DCUT:
                contact_pair.add((i,j)); contact_degree[i]+=1; contact_degree[j]+=1

    # METRIC A: top-L pair precision ---
    elig=[(mapped[x],mapped[y]) for x in range(len(mapped)) for y in range(x+1,len(mapped)) if abs(mapped[x]-mapped[y])>=SEP]
    nc=len(contact_pair); npairs=len(elig); base=nc/npairs if npairs else float("nan"); Ltop=len(mapped)
    prec_mip=np.mean([1.0 if p in contact_pair else 0.0 for p in sorted(elig,key=lambda p:-MIp[p])[:Ltop]])
    prec_cp =np.mean([1.0 if p in contact_pair else 0.0 for p in sorted(elig,key=lambda p:-(conservation[p[0]]*conservation[p[1]]))[:Ltop]])

    # METRIC B/C ---
    mm=np.zeros(L,bool); mm[mapped]=True
    B_s=spear(s_i[mm],contact_degree[mm]); B_c=spear(conservation[mm],contact_degree[mm])
    C_sc=spear(s_i,conservation); C_si=spear(s_i,inv_tol)

    print("\n===== RESULTS (PF13354) =====")
    print(f"Meff = {Meff:.1f}   mapping coverage = {coverage}/{L}")
    print(f"[A] top-L MIp precision = {prec_mip:.3f} | conservation-product precision = {prec_cp:.3f} | contact base rate = {base:.3f}   (L={Ltop}, contacts={nc}, pairs={npairs}, sep>={SEP})")
    print(f"[B] Spearman(s, contact_degree) = {B_s:+.3f}  vs  Spearman(conservation, contact_degree) = {B_c:+.3f}")
    print(f"[C] Spearman(s, conservation) = {C_sc:+.3f}   (s vs inv-tolerance: {C_si:+.3f})")
    np.savez("data/pfam/pilot_coupling_PF13354.npz", weights=weights, MIp=MIp, s_i=s_i,
             contact_degree=contact_degree, conservation=conservation, inv_tol=inv_tol,
             mapped=np.array(mapped), Meff=Meff, coverage=coverage,
             prec_mip=prec_mip, prec_cp=prec_cp, base=base, B_s=B_s, B_c=B_c, C_sc=C_sc)
    print("saved data/pfam/pilot_coupling_PF13354.npz", flush=True)

if __name__=="__main__":
    main()
