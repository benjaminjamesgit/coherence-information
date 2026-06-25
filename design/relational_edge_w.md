# D2 Relational (Edge-Valued w) -- Foundations, Architecture, Build Plan

Standing reference for the D2 relational build. Claude Code may not have access to
Benjamin's source corpus, so this transcribes the necessary formalism and the
philosophical foundations that govern design choices. `pre_registration.md` + git HEAD
remain AUTHORITATIVE for state; this doc orients. Do not re-derive from scratch; do not
reintroduce excluded constructs (especially DCA / sparse-causal estimators -- see Sec 3, 9).

---

## 0. One-paragraph orientation

Node-valued per-position `w` is RETIRED (it failed the hardened persistence bar on two
families). The coherence signal in proteins is intrinsically RELATIONAL (coevolutionary
coupling), so D2's `w` is now EDGE-VALUED: a weight on position-PAIRS. The R2-edge premise
(two philosophically-distinct, dense estimators converge on the edge graph) PASSES on both
pilot families. The build now extends the Metacoherence signatures (R1/R2/R3/M5) to edges,
under corpus constraints: dense-not-sparse, compression-as-estimator, graded-not-binary
intervention, no correspondence-oracle.

---

## 1. CIT formalism (the equations)

Shannon entropy:           H(X)      = - sum_x p(x) log p(x)
Coherence-weighted entropy: H_w(X)   = sum_x p(x) w(x) [ -log p(x) ],   w: X -> [0,1]
Coherence-weighted MI:      I_w(X;Y) = sum_{x,y} p(x,y) w(x) log[ p(x,y) / (p(x) p(y)) ]

Boundary condition: when w(x) = 1 for all x, every weighted quantity collapses EXACTLY to
its Shannon counterpart. This is the license for CIT as a generalization, not a replacement
(`tests/test_shannon_recovery.py` enforces it). `w(x)` = the expected fraction of symbol x's
contribution to recursive structural stability.

Induction pipeline (how w is obtained from data):

    stream  ->  C_hat (proxy K)  ->  rho(x) (ablation A)  ->  w(x) = sigma(beta * rho(x))

with `beta = 4.0` LOCKED, sigma the logistic. Proxies K estimate a coherence scalar C_hat;
ablations A attribute it to features as rho; the sigmoid maps relevance to a bounded weight.

---

## 2. Coherence Engine kernel (only what this build needs)

Coherence C is a BOUNDED SCALAR: the degree to which a system reinforces its own structural
organization across RECURSIVE interactions/scales. Two facts govern this build:

1. C is empirically estimable by COMPRESSION: "compression-based approximations capture the
   degree to which a configuration contains recursively recoverable structure." => our
   compression estimator (K_comp, Sec 5) is the corpus-canonical way to estimate C, not a
   mere convenience.
2. Coherence CURVATURE (Delta^2 C = second difference of C along a trajectory) is the
   ARBITRATION / SELECTION quantity, and it is what replaces binary intervention (Sec 3).
   It governs DYNAMICS (R3, R1), not the static pairwise measure.

State S = (X, C, Omega, eta, lambda): X configuration; C coherence density; Omega spectrum of
possibility (feasible coherence-increasing trajectories); eta adaptation rate; lambda leakage.
You will rarely need the full update equation here; you WILL need: bounded-scalar C,
compression-estimability, recursive/multi-scale, curvature-for-intervention.

---

## 3. Philosophical foundations CC must encode (each changes a design choice)

These are not flavor. Each forecloses or mandates a concrete build decision.

P1. CONTINUITY > DISCRETENESS. Discreteness is a derivative artifact of a continuous
    coherence field; "the timestamp of an event is a derivative artifact." The 21-residue
    alphabet is the substrate's OWN quantization, which is acceptable: CIT's formal slice is
    deliberately discrete-alphabet (continuous alphabets are deferred future work). DESIGN:
    prefer dense/relational representations over discretizing cuts.

P2. RELATIONS > OBJECTS. Coherence is borne by RELATIONS (couplings), not OBJECTS (positions).
    DESIGN: w is edge-valued (Sec 4), not per-position.

P3. DENSE FIELD, NOT SPARSE CAUSAL GRAPH. Coupling is "a field of shifting couplings," not a
    fixed wiring diagram; the sparse directed cut is "a hallucination made diagrammatic,"
    internal precision mistaken for external truth (the Pearl critique). DESIGN: EXCLUDE DCA,
    inverse-covariance, precision-matrix, and any direct-vs-indirect sparsifier as an
    estimator OR validation standard. They import the critiqued paradigm and repeat the
    correspondence-oracle error. DCA may return ONLY later as a NON-adjudicating
    "Pearlian-contrast" diagnostic (does the sparse cut discard real coupling? divergence is
    the finding, never DCA as truth). The stance is "refactor, not discard."

P4. COMPRESSION IS THE COHERENCE ESTIMATOR (Sec 2.1). DESIGN: K_comp (MDL/codelength) is a
    first-class, corpus-canonical estimator; its convergence with the information-theoretic
    MIp is the R2 cross-paradigm test.

P5. GRADED, NOT BINARY INTERVENTIONS. The corpus replaces Pearl's binary "do" operator with
    GRADIENT-based interventions and Delta^2 C curvature. DESIGN: R3-edge structural
    intervention MUST be a graded selection-pressure sweep (a coherence gradient), NOT an
    on/off do-operation with a single ||Delta w|| ratio. Re-importing binary-do re-imports the
    exact Pearlian logic excluded in P3.

P6. NO CORRESPONDENCE-ORACLE. Validation never measures w against an external truth label.
    Comparison-compressions (Pfam conservation, PDB contacts, later DCA) ENTER as "one more
    compression" but NEVER adjudicate; convergence and divergence are both findings.

---

## 4. Architecture: edge-valued w

DEFINITION. The edge weight w(i,j) on a position-pair (i,j) is recast as the CIT per-symbol
weight on the JOINT pair-symbol (x_i, x_j) over the product alphabet A x A (|A| = 21, so 441
joint symbols). This keeps edge-w INSIDE the existing H_w / I_w machinery -- it is an
EXTENSION (CIT on pair-features), not a fork. Bounded [0,1] inherits trivially. Shannon
recovery at w=1, coarse-graining consistency, and monotonicity are to be VERIFIED in the
formal-admissibility step (Sec 7).

ESTIMATORS (edge analogs of the K-proxies; DENSE paradigm only):
- K_MI   = APC-corrected mutual information (MIp): statistical / Shannon plug-in.
- K_comp = KT/MDL codelength coupling: algorithmic / description-length.
- (future) K_pred = a predictive coupling (learned, not counted) -- adds a third, genuinely
  distinct "what counts as structure" to harden R2 to the full cross-philosophy standard.
EXCLUDED: DCA / inverse-covariance / direct-coupling (P3).

METACOHERENCE SIGNATURES, on edges:
- R2-edge (DONE): distinct dense estimators converge on the edge graph, confound-controlled.
- R1-edge: high edge-w predicts coupling PERSISTENCE -- compensatory/coupled substitution
  (the pair stays mutually constrained while residues turn over); conservation-INDEPENDENT.
- M5-edge: admissibility partition = contact pairs (bearing) vs non-contact pairs (noise),
  AUROC of each estimator vs conservation-product and burial-product, long-range emphasis.
- R3-edge: GRADED structural intervention (selection-pressure sweep) reorganizes edge-w;
  interpretive intervention (BLOSUM-equivalence relabel) leaves it invariant.

---

## 5. Equations CC needs (self-contained; numpy + math.lgamma, scipy is ABSENT)

Sequence reweighting (controls phylogenetic redundancy):
    w_seq(s) = 1 / |{ s' : seq_identity(s, s') >= 0.80 }|,   Meff = sum_s w_seq(s)
Pair/marginal frequencies use these weights + a pseudocount.

APC-corrected MI (MIp), per column pair (i,j):
    MI(i,j)  = sum_{a,b} f_ij(a,b) log[ f_ij(a,b) / (f_i(a) f_j(b)) ]
    APC(i,j) = ( MI(i,.) * MI(.,j) ) / MI(.,.)        (row-mean * col-mean / grand-mean)
    MIp(i,j) = MI(i,j) - APC(i,j)
(MIp is REUSED from the saved coupling .npz -- never recompute it.)

KT (Krichevsky-Trofimov, Dirichlet-1/2) stochastic-complexity codelength of counts
n = (n_1..n_A), N = sum n_a, in bits:
    L_KT(n) = -[ sum_a (lgamma(n_a + 1/2) - lgamma(1/2))
                 - (lgamma(N + A/2) - lgamma(A/2)) ] / ln(2)

K_comp (MDL/compression edge coupling), marginal-relative:
    K_comp(i,j) = L_KT(marg_i) + L_KT(marg_j) - L_KT(joint_ij)
where marg_i is the 21-bin column-i count vector and joint_ij is the 441-bin joint count
vector. This is the description-length analog of MI; the KT complexity penalty on the
441-symbol joint (vs 21-symbol marginals) is what makes it ALGORITHMICALLY distinct from
plug-in MI (independent pairs score ~0/negative under the penalty, where MI would not).

Partial Spearman (confound control), x,y controlling a set Z = {conservation-product,
burial-product}: rank-transform all; build the correlation matrix; invert (pinv) to the
precision matrix P; partial = -P[x,y] / sqrt(P[x,x] P[y,y]).

---

## 6. Locked specs / pins (bit-exact-verified)

- MATRIX: match-state columns (Stockholm CASE convention) with gap-fraction < 0.5 on the
  seed-0 subsample = `np.random.default_rng(0).choice(n_full, 2000, replace=False)` (sorted).
  Encode amino acid -> 0..19; gap and any non-standard -> 20. (21 symbols.)
- REWEIGHTING: 80% identity, w_seq = 1/neighbor-count; report Meff.
- K_MI: APC-MIp, reused from the saved `pilot_coupling_{ACC}.npz`. DO NOT recompute.
- K_comp: KT codelength as Sec 5; numpy + math.lgamma only.
- CONTACTS: Cb-Cb (Ca for Gly) < 8.0 A, |i - j| >= 5; long-range |i - j| >= 12.
- BURIAL: `Bio.PDB.HSExposure.HSExposureCB` `EXP_HSE_B_U`, computed on the SAME model whose
  residues are mapped (the stale-residue bug is fixed; assert NaN count == L - coverage).
- PDB->COLUMN MAP: BLOSUM62 global alignment (open -11, extend -1) of the column-majority
  consensus to the PDB chain sequence.
- FAMILIES (PILOTS, list NOT locked): PF13354 / 1djc:A (a-b/a+b, L=248, cov 244);
  PF00026 / 4y9w:A (all-beta, L=312, cov 293). Selection rule in pre-reg commit b8de3f1.
- TOOLING: biopython + numpy<2 live in the repo `.venv`; scipy is ABSENT (use math.lgamma).
  data/ is gitignored -- never commit data blobs.

---

## 7. Build status + plan

DONE (verified):
- framing-S (per-position, factorized proxies) is EMPTY on real alignments.
- node-valued w RETIRED -- fails the hardened phylo bar on BOTH families.
- R2-edge PREMISE PASSES both families: Spearman(K_MI, K_comp) long-range +0.542 (PF13354),
  +0.745 (PF00026), both >= 0.5 (the +0.540/+0.748 figures are the burial-defined-subset
  long-range raw); STRENGTHENS under partialling conservation-product AND burial-product
  (+0.583->+0.651, +0.775->+0.852); consensus edges out-predict either alone on contacts
  (~11x base). (Recorded at git b28aefe.)
- FORMAL-ADMISSIBILITY (extension-not-fork) PASSES both families/both estimators (A-F;
  adversarially verified, estimators bit-exact to saved): A boundedness, B Shannon recovery at
  w=1 (|dH|=|dI|=0.0), C coarse-graining (Dayhoff-6: K_MI 0.966/0.980, K_comp 0.865/0.845, all
  >=0.7), D monotonicity, E within-class relabel invariance (=1.0), F 100-bootstrap stability
  (K_MI 0.993/0.993, K_comp 0.991/0.986, all >=0.8). The pair-OVERLAP risk broke none.
  TWO OPEN FOLLOW-UPS: (i) check B is tautological as-coded + the I_w 441-joint-vs-21-marginal
  weighting convention is unpinned off w=1 -- WHERE the edge weight attaches in I_w(X_i;X_j) is
  open; (ii) the overlap / partition-of-unity ACCOUNTING is NOT yet probed. (Recorded at the
  step-2 result commit.)

NEXT (each PRE-REGISTERED before run; Benjamin chooses order):
1. RESOLVE the two admissibility follow-ups: pin the I_w-on-edges weighting convention (441-joint
   vs 21-marginal) + rewire check B through cit/information.py; and a partition-of-unity /
   edge-OVERLAP accounting check (each position in L-1 pairs).
2. R1-edge: does high edge-w predict compensatory/coupled substitution (coupling persistence)?
   Conservation-independent. The load-bearing Adaptive-Realism cash-out on edges.
3. M5-edge: contact-vs-non-contact AUROC across more families; MUST control burial-product
   (it beats MIp on PF13354). The edge admissibility gate.
4. R3-edge: GRADED selection-pressure sweep (P5) -- structural reorganizes edge-w, interpretive
   (BLOSUM relabel) does not. NEVER binary do-operation.
5. HARDEN R2: add K_pred (predictive estimator) for the full 3-paradigm convergence.

DISCIPLINE: pre-register (thresholds fixed) -> commit+push pre-reg -> run -> report -> HOLD.
Two pilot families until Benjamin locks a list. No full grid before pilot confirmation +
sign-off. Reuse saved matrices/MIp. ASCII-only in code payloads.

---

## 8. Future explorations

- RECURSIVE / MULTI-SCALE edge-w: pairwise is FIRST-ORDER (one scale); coherence is
  reinforcement across recursive scales (Sec 2). The final relational measure may need
  higher-order/network structure (couplings of couplings, motifs). Do NOT lock pairwise as
  the final measure.
- DCA as a refactored "Pearlian-contrast" diagnostic (P3): operationalize the Pearl critique
  -- does the sparse direct-coupling cut discard real (long-range/indirect) coupling that the
  dense field retains? Divergence = finding. Never adjudicates.
- NON-CONTACT high-coupling as allostery / long-range dynamics: an R1-edge QUESTION, not
  noise -- but held at CIT's falsifiable tier (no unfalsifiable "indirect is real" license).
- CONTINUOUS-ALPHABET / quantization extension of CIT (the corpus defers this; relevant if
  the substrate is ever treated continuously rather than as 21 discrete residues).

---

## 9. Guardrails -- what NOT to do

- Do NOT introduce DCA / inverse-covariance / precision-matrix / graphical-model estimators as
  an estimator or validation standard (P3). Dense estimators only.
- Do NOT use binary do-operations for R3; use graded sweeps (P5).
- Do NOT treat the contact map as the totality of coupling -- it is ONE sparse cut.
- Do NOT validate edge-w against an external oracle; comparison-compressions never adjudicate (P6).
- Do NOT lock the family list or run a full grid before pilot confirmation + Benjamin sign-off.
- Do NOT let "indirect coupling is real" become an unfalsifiable license -- keep the falsifiable tier.
- Do NOT recompute MIp (reuse the saved npz); do NOT commit anything under data/.
