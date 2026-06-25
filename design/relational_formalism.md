# Relational Coherence-Weighted Information -- The Corrected Formalism

The formal object for D2's EDGE-VALUED `w`. This SUPERSEDES the prior "edge-w = CIT per-symbol
weight on the 441-symbol joint pair-symbol" definition, which is RETRACTED (Sec 10). Authoritative
for state remain `pre_registration.md` + git HEAD; this doc derives the object and argues its
admissibility (each property with the ARGUMENT, not just the claim). ASCII only; numpy +
`math.lgamma` for any apparatus; canonical `cit/information.py` for all raw information quantities.

---

## 1. Objects

Positions 1..L are discrete random variables X_1..X_L over a common alphabet A (|A| = 21: the 20
amino acids + a gap/non-standard class). The substrate is the column-major alignment matrix.

The relational structure is the DENSE complete graph on positions:

    E = { (i, j) : 1 <= i < j <= L }      |E| = L(L-1)/2

No sparsification, no direct-vs-indirect cut (P3: coupling is a dense field, not a wiring
diagram; DCA / inverse-covariance are EXCLUDED as estimator and as validation standard).

The RAW pairwise mutual information of an edge is the classical quantity

    I(X_i; X_j) = sum_{a,b in A} p_ij(a,b) log2[ p_ij(a,b) / (p_i(a) p_j(b)) ]   >= 0

computed via the CANONICAL routine `cit/information.py:coherence_weighted_mutual_information`
with the joint pmf p_ij (shape 21x21, reweighted counts normalized) and weights = ones(21). At
ones the canonical routine returns exactly classical MI, so I(X_i; X_j) is a genuine call into
the same machinery single-source CIT uses -- NOT a re-implementation (the step-2 tautology trap).

---

## 2. The relational coherence-weighted functional

The edge weight w(i, j) in [0, 1] grades how much each RELATION (edge) contributes to recursive
structural stability -- the edge analog of single-source w: X -> [0, 1]. The coherence-weighted
information of the graph is the weighted sum of edge couplings:

    I_w_rel  =  sum_{(i,j) in E} w(i,j) * I(X_i; X_j)                                   (1)

This is the I_w analog: it weights the RELATION's information, not a symbol's. It is a scalar
functional of the weight field w over E.

BOUNDED relational coherence (the Coherence-Engine bounded scalar C in [0, 1]):

    C_rel  =  I_w_rel / sum_{(i,j) in E} I(X_i; X_j)                                    (2)

i.e. the FRACTION of the graph's total pairwise coupling that the weight field retains.

NODE-INDUCED coherence -- the edge field induces a per-position scalar (the cross-scale link
from edges back to nodes):

    c_i  =  sum_{j != i} w(i,j) * I(X_i; X_j)                                           (3)

---

## 3. The handshake identity (overlap / non-partition accounting)

The pair representation is NOT a partition of the stream: each position i participates in L-1
edges, so summing per-node loads double-counts each edge. This was the previously-UNPROBED risk.
It is resolved exactly by the handshake:

    sum_{i=1}^{L} c_i
      = sum_i sum_{j != i} w(i,j) I(X_i; X_j)
      = sum_{(i,j) in E} w(i,j) I(X_i; X_j) * [ contributes once as (i in pair) + once as (j in pair) ]
      = 2 * sum_{(i,j) in E} w(i,j) I(X_i; X_j)
      = 2 * I_w_rel                                                                     (4)

ARGUMENT: w(i,j) and I(X_i; X_j) are symmetric in i, j (the edge is undirected; I is symmetric).
Edge {i, j} appears in c_i (as the j-term) and in c_j (as the i-term) and in no other node-load.
So each edge's contribution is counted exactly twice in sum_i c_i. The factor of 2 is the
handshake lemma of graph theory (sum of degrees = 2|edges|) carried through a weighted sum. This
identity is the bookkeeping that makes node-induced coherence consistent with the edge functional
despite the overlap -- there is no leakage or double-spend, only a known factor of 2.

---

## 4. Induction (formal / induced split)

How w(i,j) is obtained from data mirrors single-source CIT's formal/induced separation:

    edge proxy K:    stream -> Chat(i,j)        (K_MI = APC-MIp, or K_comp = KT/MDL coupling)
    edge relevance   rho(i,j)                   (marginal-relative -- what APC/MIp already deliver)
    w(i,j) = sigma(beta * z(rho(i,j))),  beta = 4.0 (LOCKED), z = standardize over eligible pairs

CRITICAL SEPARATION (do not conflate): the FORMAL object I_w_rel (eq. 1) is built on RAW
I(X_i; X_j) -- a clean classical quantity with a clean Shannon boundary. The WEIGHT w is INDUCED
from MARGINAL-RELATIVE proxies (APC-MIp and KT/MDL coupling are both beyond-marginal -- they
subtract or penalize what the independent marginals already explain). This is exactly the split
single-source CIT already uses: formal H_w / I_w on raw p, with w induced from marginal-relative
K-proxies. The formal object stays Shannon-anchored; the relevance signal lives in w.

---

## 5. Recursive / multi-scale generalization

Pairwise coupling is order k = 2 -- the FIRST recursive order, made explicit. The corpus's
coherence is reinforcement across recursive scales, so the measure generalizes to hyperedges:

    w(S) on k-subsets S,  weighting the order-k interaction measured by total correlation TC(S):
    C_rel_k  =  sum_{|S| = k} w(S) TC(S) / sum_{|S| = k} TC(S)                          (5)

k is the recursive-scale axis; k = 2 recovers eqs. (1)-(2) with TC({i,j}) = I(X_i; X_j). Higher
orders are DEFERRED (build k = 2 now); pairwise is NOT locked as the final measure.

---

## 6. Admissibility -- each property WITH its argument

A relational generalization of CIT is admissible if it is bounded, monotone, recovers Shannon at
the boundary, is invariant to meaning-preserving relabelings, behaves consistently under
coarse-graining, is recursively/representationally stable, and is empirically derivable. Each
below states the property AND the argument that it holds for the object of Secs 2-4.

(A) BOUNDEDNESS. C_rel in [0, 1]; I_w_rel in [0, sum I].
    ARGUMENT: every w(i,j) in [0,1] and every I(X_i; X_j) >= 0 (MI is non-negative). So each term
    w(i,j) I(X_i; X_j) lies in [0, I(X_i; X_j)], and the sum lies in [0, sum I]; dividing by sum I
    (when > 0) gives C_rel in [0, 1]. The bound is TIGHT: w == 0 gives 0, w == 1 gives 1.

(B) MONOTONICITY. I_w_rel is non-decreasing in each w(i,j); raising one weight by delta raises
    I_w_rel by exactly delta * I(X_i; X_j).
    ARGUMENT: I_w_rel is LINEAR in the weight field (eq. 1), with non-negative coefficients
    I(X_i; X_j). The partial derivative d I_w_rel / d w(i,j) = I(X_i; X_j) >= 0 is constant in w.
    There is no interaction between weights, so no rank inversions can arise from a single-weight
    increase. (This is what S4 verifies analytically.)

(C) SHANNON RECOVERY (the generalization license -- a REAL reduction, not a tautology).
    At w(i,j) = 1 for all edges, I_w_rel = sum_{(i,j) in E} I(X_i; X_j) = the total pairwise
    coupling of the graph, and C_rel = 1.
    ARGUMENT: substitute w == 1 into eq. (1). The weight drops out and what remains is a sum of
    CANONICAL classical MI values -- each computed by the same `cit/information.py` routine at its
    own w = ones boundary. This is non-trivial in two senses the retracted object failed: (i) the
    reduction target (sum of pairwise MI) is a meaningful classical quantity, the graph's total
    pairwise coupling, not an artifact; (ii) the recovery is exercised through the canonical
    weighted routine, so it tests the actual machinery -- and crucially the functional RESPONDS to
    w off the boundary (at w != 1, I_w_rel != sum I), which a hardcoded-ones tautology never does.
    (S1 verifies both the boundary AND the non-trivial weight response.)

(D) NON-COLLAPSE (the relational signature -- the property the retracted object LACKED).
    For an (approximately) independent pair, I(X_i; X_j) ~ 0, so the edge contribution
    w(i,j) I(X_i; X_j) ~ 0 REGARDLESS of the marginal entropies H(X_i), H(X_j).
    ARGUMENT: I_w_rel weights MUTUAL INFORMATION, which is zero at independence by construction.
    Contrast the retracted object: single-source H_w on the merged 441-symbol node scores
    ~ H(X_i) + H(X_j) >> 0 at independence (it weights joint symbol-VALUES / surprisal, which do
    not vanish at independence). So the corrected object measures the RELATION (zero coupling ->
    zero contribution) where the old one measured merged-marginal surprisal. (S2 demonstrates the
    split numerically on low-I vs high-I pairs.)

(E) RELABEL / DOMAIN-TRANSLATION INVARIANCE. At fixed w, permuting amino-acid identities within
    meaning-preserving (Dayhoff / BLOSUM-equivalence) classes leaves I_w_rel unchanged.
    ARGUMENT: I(X_i; X_j) is a function of the JOINT DISTRIBUTION over symbol pairs, invariant
    under any bijective relabeling of A applied jointly to both margins (MI is a property of the
    coupling, not of symbol identities). A within-class permutation is such a bijection. Since
    I_w_rel is a w-weighted sum of these invariant terms and w is held fixed, it too is invariant.
    This is a POSITIVE result: the estimator is STRUCTURAL, not symbolic, and it pre-validates the
    R3 interpretive arm (a meaning-preserving relabel must leave edge-w essentially unmoved).
    (S6 verifies invariance to < 1e-9.)

(F) COARSE-GRAINING CONSISTENCY (with the node-merge rule). Two coarse-grainings must agree in
    rank with the fine object:
    (F1) ALPHABET coarse-graining: remap A to Dayhoff-6 classes, recompute I on the coarse
    alphabet, and require rank-consistency of the edge ordering with the full-alphabet object.
    ARGUMENT: coarsening the alphabet is a deterministic function of the symbols, which by the
    data-processing inequality cannot increase any I(X_i; X_j); admissibility asks only that it not
    REORDER the edges (the coupling structure survives a coarser lens). Verified empirically
    (step-2 reported Dayhoff-6 Spearman 0.85-0.98); a low value would be an alphabet-FRAGILITY
    finding, recorded honestly, not silently passed.
    (F2) NODE-MERGE coarse-graining (c-merge, the graph operation): merging positions i, j into a
    super-node DROPS the internal edge (i, j), UNIONS the external edges, and combines parallel
    weights to the same neighbor by a COUPLING-WEIGHTED AVERAGE
        w(merged, n) = [ w(i,n) I(X_i; X_n) + w(j,n) I(X_j; X_n) ] / [ I(X_i; X_n) + I(X_j; X_n) ].
    ARGUMENT: this rule preserves the external coherence budget -- the merged node's load equals
    the sum of the parts' external loads (the coupling-weighted average times the summed coupling
    returns the summed weighted coupling), so I_w_rel restricted to external edges is conserved up
    to the dropped internal edge. (c-merge is stated here; its empirical commitment is a later
    step, flagged among the open choices.)

(G) RECURSIVE / RESAMPLING STABILITY. The edge ordering is stable across ortholog bootstraps
    (resample sequences, re-reweight, recompute), and the node-induced loads c_i are consistent
    with I_w_rel via the exact handshake (eq. 4) at every w.
    ARGUMENT (stability): the estimator is a smooth function of reweighted pair frequencies, which
    concentrate as Meff grows; rank stability is the empirical signature (step-2 reported
    100-bootstrap mean Spearman 0.99). ARGUMENT (recursive consistency): the handshake identity is
    EXACT and w-independent, so the cross-scale map edges -> nodes -> (sum) never drifts from the
    edge functional -- a structural, not merely empirical, stability. (S3 verifies the handshake to
    < 1e-9 at w == 1, random w, and induced w.)

(H) EMPIRICAL DERIVABILITY. w is induced from data (Sec 4) by marginal-relative proxies through
    the LOCKED sigmoid (beta = 4.0); the formal object reads RAW I. Both are computable from the
    alignment with numpy + `math.lgamma` (no scipy, no DCA). This is the same derivability standard
    single-source CIT meets.

---

## 7. Open choices (the stress-test INFORMS; Benjamin DECIDES)

(c1) NORMALIZER for C_rel (eq. 2): sum I (recommended -- "fraction of coupling retained", the
     natural [0,1] reading) vs |E| (mean weighted coupling per edge) vs max (peak-relative). S8
     reports C_rel under all three at induced w, both families, as evidence.

(c3) BASE of the formal object: RAW I (recommended -- clean classical boundary, all terms >= 0,
     C_rel cleanly in [0,1]) vs MIp (beyond-marginal, sharper on real coupling but no clean Shannon
     boundary and individual terms can be negative -> C_rel can leave [0,1]). S7 reports I_w_rel at
     w == 1 under both bases and counts negative-MIp edges, as evidence.

(c-merge) NODE-MERGE rule (Sec 6 F2): stated as the coupling-weighted average; needed before the
     coarse-graining commitment is locked.

These are NOT decided here. The stress-test produces the evidence; Benjamin rules.

---

## 8. What is RETRACTED, and why this is the correction

RETRACTED: "edge-w = the CIT per-symbol weight on the JOINT pair-symbol (x_i, x_j) over the 441
product alphabet, an EXTENSION not a fork", together with the step-2 admissibility PASS that
verified it. Four reasons (full statement in the pre-reg 2026-06-25 step-3 amendment):
  1. It COLLAPSES to single-source node-w on a merged 441-symbol node -- weights joint symbol
     VALUES, not the RELATION. Not relational (violates P2). Property (D) above is exactly what it
     fails: it does not vanish at independence.
  2. Canonical I_w weights the 21-symbol SOURCE MARGINAL; a 441-length weight is not even
     shape-admissible (fails `_check_weights`).
  3. The corpus defines w only single-source and is SILENT on edge weighting -- a real FORMAL GAP.
  4. The step-2 "PASS" was FALSE COMFORT (check B hardcoded `np.ones_like`; E/F same-code recompute;
     the pair-overlap risk never probed).

THE CORRECTION weights the RELATION (eq. 1), is genuinely relational (property D), handles the
overlap by the exact handshake (eq. 4, the previously-unprobed risk now closed), and has a REAL
Shannon reduction exercised through the canonical routine (property C). The pre-registered
stress-test S1-S8 checks these against two families before any claim of admissibility is recorded.
