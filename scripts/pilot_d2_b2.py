#!/usr/bin/env python3
"""D2 beta-line check B2 (pre-registered 2026-06-24, pre_registration.md): GRAPH-STRUCTURAL
node projections of the MIp coupling graph -- the LAST node-valued attempt before an edge-valued
w (branch A) is forced. Motivated by B'-FAIL on naive partner-aggregations. REUSES the existing
MIp .npz (no recompute) + the B' burial artifact. Standalone; outputs -> data/pfam/ (gitignored).

PINS (from the B2 pre-registration):
  weighted adjacency W = max(APC-MIp, 0), diagonal 0.
  g_eig  = eigenvector centrality (leading eigenvector of W; numpy).
  g_pr   = PageRank (power iteration, damping 0.85; numpy).
  g_topL = per-position membership count in the top-L MIp pairs (L = #mapped positions; pairs over
           mapped positions, |i-j| >= 5 -- the same top-L set as pilot check A; the A->node bridge).
  bar = identical to B': burial = HSExposureCB on 1djc:A (reused from pilot_bprime_PF13354.npz);
  B2-PASS iff at least one projection's partial-Spearman(g, contact_degree | burial) is BOTH > 0
  AND > conservation's burial-controlled partial (computed in-run).
"""
import numpy as np
COUP="data/pfam/pilot_coupling_PF13354.npz"; BP="data/pfam/pilot_bprime_PF13354.npz"
SEP=5; DAMP=0.85

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
    d=np.load(COUP); MIp=d["MIp"]; contact_degree=d["contact_degree"]; conservation=d["conservation"]
    mapped=sorted(int(x) for x in d["mapped"]); L=MIp.shape[0]
    burial=np.load(BP)["burial"]  # HSExposureCB EXP_HSE_B_U on 1djc:A, aligned to L (nan unmapped)

    W=np.maximum(MIp,0.0); np.fill_diagonal(W,0.0)

    # g_eig: leading eigenvector of W (symmetric -> eigh)
    val,vec=np.linalg.eigh(W); v=vec[:,-1]; v=v*np.sign(v.sum() if v.sum()!=0 else 1.0)
    g_eig=np.abs(v)

    # g_pr: PageRank, damping 0.85, power iteration
    rs=W.sum(axis=1); S=np.zeros_like(W)
    nz=rs>0; S[nz]=W[nz]/rs[nz,None]; S[~nz]=1.0/L  # dangling -> uniform
    pr=np.full(L,1.0/L)
    for _ in range(1000):
        nxt=DAMP*(S.T@pr)+(1-DAMP)/L
        if np.abs(nxt-pr).sum()<1e-12: pr=nxt; break
        pr=nxt
    g_pr=pr

    # g_topL: node degree in pilot-A's top-L coevolution graph (mapped, sep>=5, L=#mapped)
    mp=mapped; elig=[(mp[x],mp[y]) for x in range(len(mp)) for y in range(x+1,len(mp)) if abs(mp[x]-mp[y])>=SEP]
    topL=sorted(elig,key=lambda p:-MIp[p[0],p[1]])[:len(mp)]
    g_topL=np.zeros(L)
    for i,j in topL: g_topL[i]+=1; g_topL[j]+=1

    mm=np.zeros(L,bool)
    for c in mapped:
        if np.isfinite(burial[c]): mm[c]=True
    cons_raw=spear(conservation[mm],contact_degree[mm]); cons_par=partial(conservation[mm],contact_degree[mm],burial[mm])

    print(f"===== B2 (PF13354) =====  positions used = {mm.sum()}  (L_top = {len(mp)} pairs)")
    print(f"conservation: raw Spearman(.,contact_degree)={cons_raw:+.3f}  partial(.|burial)={cons_par:+.3f}\n")
    projs={"g_eig":g_eig,"g_pr":g_pr,"g_topL":g_topL}; passers=[]; out={}
    for nm,g in projs.items():
        raw=spear(g[mm],contact_degree[mm]); pa=partial(g[mm],contact_degree[mm],burial[mm])
        beats=(pa>0) and (pa>cons_par)
        if beats: passers.append(nm)
        out[nm]={"raw":raw,"partial":pa,"beats_cons":bool(beats)}
        print(f"  {nm:7s}: raw Spearman(.,contact_degree)={raw:+.3f}  partial(.|burial)={pa:+.3f}  >0 & >cons? {beats}")
    verdict="B2-PASS" if passers else "B2-FAIL"
    print(f"\nVERDICT: {verdict}  (projections beating conservation on burial-controlled partial: {passers or 'NONE'})")
    print("DECISION: " + ("Sec 6.2 NODE-valued w SURVIVES -> node-valued joint-proxy design (confirm on >=1 more family before lock)"
          if passers else "node-projection space EXHAUSTED -> EDGE-valued w (branch A) FORCED -> corpus-admissibility check before any edge design; escalate"))
    np.savez("data/pfam/pilot_b2_PF13354.npz", g_eig=g_eig, g_pr=g_pr, g_topL=g_topL, burial=burial,
             cons_partial=cons_par, results=str(out), verdict=verdict)
    print("saved data/pfam/pilot_b2_PF13354.npz")

if __name__=="__main__":
    main()
