# CLAUDE.md — coherence-information (CIT)

Repo-scoped instructions for Claude Code. The global ACRE operating instructions
load separately and govern register and posture; this file governs only this repo.
On conflict: Benjamin live > global ACRE > this file > code comments.

## Boot procedure (run on every fresh session, before any change)

1. Read `README.md` (status table = version history and current state).
2. Read `pre_registration.md` (the locked-commitment record; authoritative over code).
3. `git log --oneline -15` and `git status` — confirm HEAD and clean tree.
4. Run the fast suite: `pytest` (defaults to fast-only). Report green/red.
5. Report state, then wait for steering. Do not edit before reporting.

For D2 relational (edge-valued w) work, read `design/relational_edge_w.md` -- foundations, specs, and guardrails (esp. DCA exclusion and graded-not-binary interventions).

## What CIT is, and why

Coherence Information Theory generalizes Shannon by attaching a bounded weight
`w(x) in [0,1]` to each source symbol, measuring that symbol's contribution to
recursive structural stability. Three formal quantities:

    H(X)      = -sum p(x) log p(x)                       (Shannon entropy)
    H_w(X)    = sum p(x) w(x) [-log p(x)]                (coherence-weighted entropy)
    I_w(X;Y)  = sum p(x,y) w(x) log[p(x,y)/(p(x)p(y))]   (coherence-weighted MI)

Boundary condition: when `w(x)=1` for all x, every weighted quantity collapses
exactly to its Shannon counterpart. This is what licenses CIT as a generalization,
not a replacement; `tests/test_shannon_recovery.py` enforces it empirically.

Why it exists: CIT is the empirical, falsifiable arm of the Recursive Coherence
corpus (T1). It is the proof of intent — the framework is "vulnerable in the right
way" only if commitments precede outcomes. The whole point is cross-proxy and
cross-ablation convergence plus noise-only falsifiability: if independent proxies
of coherence did not converge, the construct would be empty. That is the claim
under test. Do not let the code drift from this; a passing suite that no longer
tests convergence is lock-in.

Weights are either user-supplied or induced from data:
`stream -> C_hat (proxy K) -> rho(x) (ablation A) -> w(x) = sigma(beta * rho(x))`.

## Current state

- Version `0.7.1` (pyproject + README + CITATION.cff; tagged 2026-06-24). v0.6 operational-theorem program COMPLETE: v0.6.0 capacity
  estimator, v0.6.1 selective coder (Thm 5.1 repaired), v0.6.2 Selective Compression empirics.
- Proxies (K_n): K1 compression-delta (zstd), K2 n-gram MDL, K3 neural prequential
  (single-layer GRU), K4 MDL-HMM (factorized-Bernoulli HMM, two-part MDL selection over
  H in {1,2,3,4}, deterministic Baum-Welch, `HMM_SEED=0`), K5 Lempel parsing (bit-level LZ76, numba).
- Ablations (A_m): A1 LOO replace-with-uniform, A2 Shapley (k=64), A3 correlation-cluster.
- Capacity (v0.6.0): `cit/capacity.py:coherence_capacity` = max_p I_w(X;Y) over the input simplex
  via deterministic projected-gradient multi-start (analytic gradient, no RNG, bit-exact); `w=1`
  recovers Shannon capacity (BSC/Z). Sec 6 fixture erratum recorded: paper's C_C(eps)=0.5(1+eps)
  is I_w@uniform, a lower bound, NOT the max (uniform not optimal for eps<1). Concavity OPEN.
- Coder (v0.6.1): `cit/coders/selective.py` — repairs Selective Compression Thm 5.1 (UNSOUND for
  non-constant w; H_w demoted to a "bits that matter" MEASURE). Corrected floor = merged-source
  entropy H(Z) (reproduce S_delta={x:w(x)>delta} exactly, collapse don't-cares). merge->entropy-code:
  bit-exact arithmetic coder (rate -> H(Z)+eps) + zstd variant. Boundary S_delta=X collapses to Shannon.
- Empirics (v0.6.2): falsifiable win-margin — selective coder compresses 31-49% below the weight-blind
  lossless rate at zero retention cost on coherence-structured sources; saving = 0 at the boundary.
  arith Delta_frac >= WIN_MARGIN=0.20 on iid/Gilbert-Elliott/TCUN substrates (calibrated like T_NOISE).
- v0.7 (cross-domain / Metacoherence; v0.7.0 D1 + v0.7.1 R1 SHIPPED + tagged `v0.7.1` 2026-06-24; cross-domain VALIDATION still in progress. **v0.7.2 D2 (Pfam) relational line CLOSED 2026-06-25 as a FALSIFICATION -- unreleased; K_comp = affine(raw MI), a theorem; within-domain coherence-beyond-MI NOT found; see the step-7 entry below. v0.7.3 OPENED = cross-domain transfer DESIGN DRAFT, OPEN; step 1 (2026-06-25) = draft updated with validated well-posedness findings (order-collapse generalization -- "higher order" relocates the collapse one order up, not an escape; the coarse-graining/RG FLOW-object escape candidate = the next THEORY problem; corpus-gap + strengthened collapse-gate + R1-persistence-hook fixes) + D-cal (synthetic transfer-machinery CALIBRATION, the cross-domain analog of D1) PRE-REGISTERED then RUN -> MACHINERY VALIDATED (readout-fix amendment: across-latent null ensemble; real_P transfer +0.99 >> null +0.06 [same encoders -> ~0 null = shared latent, not artifact], real_H +0.15 ~= null +0.04 [flat measure BLIND to the pure-higher-order coalition, which carries the latent at 3rd order], generic stats matched <0.02) -> the FLOW-object target is set (transmit H: real_H >> null_H); scripts/dcal.py. STEP 2 (2026-06-25) = THE PINCER (generic-horn [transmits trivially, empty] vs correspondence-horn [wiring needs a prior-importing map]) + the COORDINATE-FREE (permutation-invariant) SHAPE-INVARIANT escape (eigenvalue spectrum / persistent homology -- no correspondence, not a scalar exponent); D-cal-2 PRE-REGISTERED then RUN -> NUANCED landing: coordinate-free transfer WORKS for PAIRWISE (AUROC_pairwise 1.000, perm-invariance 2e-15, generic matched <0.02 -> the correspondence horn IS dodgeable, which D-cal could not show) for HIGHER-ORDER the eigenvalue-SPECTRUM invariant gave AUROC_HO 0.684. CORRECTED step 2b (independently reproduced): the 0.684 is a coordinate-free SPECTRAL-INSTRUMENT ceiling, NOT structural -- the higher-order STRUCTURE transmits at AUROC 1.000 WITH correspondence (W_HO matrix aligned by feature index; encoded-vs-latent-truth also 1.000); the spectrum discards the topology (which features in which triple), keeping only the generic strength multiset. The earlier 5-invariant fair-shot tested only SPECTRAL invariants -> confirmed the spectral ceiling but MISLABELED it as structural. So the PINCER is NOT confirmed for higher-order; the question is OPEN with the coordinate-free INSTRUMENT as the limiter (the 1.0 ceiling is WITH correspondence = horn 2). NEXT (step 2b Phase 2) = a RICHER coordinate-free TOPOLOGICAL invariant (H0 barcode / Betti-1 curve / triangle-weight distribution, numpy-only, NO PH lib) to test whether 0.68->1.0 closes (escape bar 0.90); scripts/dcal2.py + dcal2_topo.py; independently verified.**): v0.7.0 D1
  BUILT + record-corrected (slices 1-3, committed `823928a` + `f1d1da3`; full v0.7 chain `d9eb3b5`..`bbd081c`). D1 generator `cit/data/hsmm_d1.py`
  (seeds 7000..7019); categorical marginal-relative K1-K5 `cit/proxies/categorical.py`; categorical A1/A2/A3
  `cit/ablations/categorical.py`; `cit/induce_cat.py`; R2 + cross-tab `cit/metacoherence.py` (incl.
  `partition_diagnostic`, the +0.43 shared-top-k bound); CI verdict job `scripts/run_metacoherence_grid.py`.
  LOAD-BEARING lock HELD: coherence on D1 is MARGINAL-RELATIVE (predictive `H_marg - H_pred`; compression via
  a TIME-SHUFFLE surrogate baseline, `SHUFFLE_SEED=0`, feature-major bit encoding). **R2 result =
  INSTRUMENT-VALIDITY, NOT a falsification (corrected at `f1d1da3`):** on D1's A1 column the proxies recover
  COMPLEMENTARY properties (K5 {A,B,C,D}, K1 {A,C}, K2/K3/K4 {A,D}); the induced-w Spearman blocks {K1,K5}
  (within +0.68) vs {K2,K3,K4} (within 0.71-0.93) split COLLINEAR with the encoder boundary (byte-stream vs
  categorical-native), so philosophy and REPRESENTATION are CONFOUNDED -> `R2>0.6` NOT YET ADJUDICABLE (not
  falsification, not vindication). PROVISIONAL (single seed 7000, T=8000=16% of locked 50k; C most
  seed-variable). BANKED: property A converges across BOTH representations + all 5 proxies. Invariant (2)
  SPLIT (substrate-MI holds / induced-w fails at A1). The representation-vs-philosophy DECOUPLING CONTROL
  (modeling-on-byte-stream crossings K3b/K2b, A1, full-T, 20 seeds) RAN (2026-06-24): terminal verdict
  INCONCLUSIVE -- necessary-NOT-sufficient. It WEAKENS the representation-artifact reading (nothing leaned byte
  at full power) but does NOT establish philosophy: K3b leans modeling confidently (20/20, median +0.51) yet was
  pre-flagged as able to for trivial flexibility reasons (twin 0.88 is consistent with representation-invariance);
  K2b -- which probes the actual factorized C-blindness -- was UNSTABLE (17/20, one seed short). A pre-registered
  read-only I_C diagnostic REJECTED a property-dependent-representation explanation (the 3 negative-Delta seeds are
  NOT high-I_C; ranks [12,1,17], Spearman -0.25 n.s.), so the K2b near-miss is genuine borderline NOISE. Option
  (e)(i) (hold-encoding-constant) stays the recorded-but-UNJUDGED next control (see 2026-06-24 amendment). A3==A1
  on D1 (Pearson singletons); pre-reg line 791 corrected (K1/K5 were NOT alphabet-agnostic). PROGRAM REFRAME (2026-06-24 amendment, epistemics NOT results): D1's role recast as ESTIMATOR
  COVERAGE-CALIBRATION vs known ground truth -- the finding is DIFFERENTIAL coverage with K5 (parsing) MOST
  COMPLETE -- ASYMMETRIC, not compositional: K5 widest aperture (A,B,C,D), modeling-trio gapped {A,D},
  compression {A,C}, A universal; the union-recovers-all is CARRIED BY K5, NOT a composition (D2/D3 action:
  weight parsing widest, treat the trio/compression as specialized/confirmatory; the ranking itself is
  provisional -- single seed 7000, 16% T). So the D1 `R2>0.6` commitment is SUPERSEDED IN STATUS (not
  deleted, not edited). R2 reclassified DIAGNOSTIC: coverage-capped -- corroborating on convergence,
  NON-FALSIFYING on divergence (0.6/0.4 stay as a convergence flag; grid unchanged, still runs). R1 (persistence)
  + the v0.6.2 selective-compression FUNCTIONAL win ELEVATED to PRIMARY cross-domain evidence (functional
  convergence -- w doing the same work -- NOT weight-vector matching). R1 SPEC GUARD (pre-registered):
  functional convergence = PER-ESTIMATOR functional validity (each w predicts persistence, clean yes/no)
  AGGREGATED, NOT cross-estimator agreement on predictions (else R2's coverage-ambiguity returns in a functional
  costume; R1 escapes the ceiling by not requiring cross-estimator AGREEMENT, not by being coverage-free).
  Eight-cell matrix needs re-derivation under R2-as-diagnostic (capstone-pending). v0.7.1 R1 BUILT + RUN + CLOSED
  as CALIBRATION (necessary-not-sufficient AND MECHANISM-CONFOUNDED): D1's regime path is emission-independent (the
  Sec 5.4 drift->transition coupling is NOT instantiated), so D1 persistence = regime-inference structure; apparatus
  `cit/persistence_d1.py` validated against ground truth; the decoder-free log-likelihood-cost magnitude is D-LED
  (20-seed disambiguation: information-sensitive WITHIN a property, concentration-biased ACROSS), and the partial
  proxy d-matrix (K1 FAILS -0.386 / K2 PASSES +0.986) makes the confound concrete (passing == weighting the sharp
  feature D, NOT tracking persistence-relevance). The concentration confound is PARKED for D2/D3 with a pre-registered
  emission-concentration-HOMOGENEITY check. D2 (Pfam, CC0) R1 PRE-REGISTERED (`df025a3`; ML per-site-rate
  substitution tolerance + the conservation-tautology confound check; two numbers flagged for the data-survey).
  D2 then ADVANCED (all committed): survey (M-CSA-seeded pool) -> conservation-tautology REWORK + RESOLUTION +
  dual-transposition REDESIGN amendments -> a framing-S premise check (the marginal-relative proxies measure EMPTY:
  K2/K3 flat) -> a COUPLING pilot = INTERMEDIATE (pairwise coevolution real + conservation-independent A/C; the
  per-position SUM projection weak B). Check B' (`scripts/pilot_d2_bprime.py`) RAN + FAILED: burial confound REAL
  (contact_degree~burial +0.78; conservation's contact prediction drops +0.43->+0.14 burial-controlled), and NO
  edge->node node-aggregation (s_max/s_top5/s_cnt) beats conservation's burial-controlled partial -> the edge->node
  projection LOSES the signal. The pre-registered B'-FAIL decision ESCALATES the Sec 6.2 per-position-w EDGE->NODE
  question (coevolution is edge-valued, induced-w is node-valued). Check B2 (graph-structural node projections of the
  MIp graph; `scripts/pilot_d2_b2.py`) RAN + PASSED NARROWLY: g_pr (PageRank, d=0.85) burial-controlled partial
  Spearman(., contact_degree|burial) = +0.151 BEATS conservation's +0.143 (g_eig +0.092, g_topL +0.052 both FAIL) ->
  Sec 6.2 NODE-VALUED w SURVIVES, edge-valued branch A NOT forced. CAVEATS: razor-thin (+0.008) on ONE family (the
  pre-reg rule REQUIRES replication on >=1 more coevolution-rich family before any node-valued lock), and the recorded
  prediction was INVERTED (g_topL failed, global PageRank flow passed). SECOND-FAMILY REPLICATION + EDGE-M5 RAN
  (`b8de3f1` pre-reg -> RESULT this entry; apparatus `scripts/run_d2_family2.py`, matrix recipe pinned BIT-EXACT to
  PF13354) on PF00026 (Asp / 4y9w:A; pure all-b aspartic protease, L=312, cov 293/312; size-floor refinement >=150 cols
  excluded the literal hit PF00024/PAN_1 as a weakly-catalytic disulfide module). RESULT = EDGE GENERALIZES, NODE does
  NOT clear the hardened bar -> MIXED, BRANCH ADJUDICATION HELD for Benjamin. EDGE: check A 0.160 vs base 0.019 PASS;
  edge-M5 PASS (MIp-AUROC 0.802 [CI 0.789-0.814] > cons-prod 0.442 AND > burial-prod 0.685; long 0.794 > 0.700). PF13354
  fold-in: MIp 0.698 BEATS conservation (0.419) but LOSES to burial (0.716) -> the edge margin OVER burial is
  family-dependent (loses on small a-b/a+b PF13354, wins on larger all-b PF00026). NODE hardened: g_pr partial|burial
  +0.127 vs phylo-cons +0.134 -> margin -0.007 (CI -0.154,+0.129 INCLUDES 0) NOT ROBUST; the B2 PF13354 g_pr pass did NOT
  replicate; winning projection UNSTABLE (g_pr PF13354 / g_topL PF00026). Strict 'node-fail generalizes' NOT literally met
  (B' beat the WEAKER entropy ref +0.091 on PF00026) but the HARDENED phylo bar FAILS. BRANCH ADJUDICATED (Benjamin):
  node-valued w RETIRED (fails the hardened phylo bar BOTH families), EDGE-valued w ADOPTED (corpus-aligned: coupling is a
  DENSE entangled FIELD, not a sparse direct-edge graph; + empirically supported). RELATIONAL BUILD step 1 PRE-REGISTERED
  (`e3e0458` pre-reg -> RESULT this entry; apparatus `scripts/r2_edge.py`): R2-EDGE premise = convergence of TWO distinct
  DENSE paradigms K_MI (APC-MIp, Shannon plug-in; reuse saved MIp) vs K_comp (MDL/KT compression edge coupling =
  joint-vs-independent codelength, marginal-relative, numpy `math.lgamma`; validated +1674 bits coupled / -27 independent);
  DCA/inverse-covariance EXCLUDED as the Pearlian cut the corpus critiques. RESULT = R2-EDGE PASS BOTH families: long-range
  Spearman(K_MI,K_comp) +0.542 (PF13354) / +0.745 (PF00026) >=0.5; CONSENSUS-edge contact precision BEATS each alone (0.242
  vs 0.131/0.086; 0.214 vs 0.160/0.150, ~11x base); and the convergence SURVIVES -- in fact STRENGTHENS -- under the
  conservation-product + burial-product control (partial +0.651 / +0.852 vs raw +0.583 / +0.775), so it is NOT the
  agree-on-conserved/buried-pairs null. Caveat: top-L Jaccard MODEST (0.15/0.24, expected for genuinely distinct estimators);
  TWO families, no grid, no lock. The edge-valued direction is now supported by cross-paradigm convergence. RELATIONAL BUILD
  step 2 = edge-w FORMAL-ADMISSIBILITY check RAN + PASSED-AS-CODED but now RETRACTED (by step 3): it verified the WRONG object
  (edge-w = CIT per-symbol w on the 441-joint pair-symbol, which COLLAPSES to single-source node-w on a merged 441-symbol node,
  weights joint symbol-VALUES not the RELATION, and is not even shape-admissible vs canonical I_w's 21-symbol source marginal)
  AND the PASS was TAUTOLOGICAL (check B hardcoded np.ones; the pre-registered pair-OVERLAP risk was never probed). RELATIONAL
  BUILD step 3 = RETRACT that object + the step-2 PASS + INSTALL the corrected RELATIONAL functional + stress-test (pre-reg
  `017a7e4` -> RESULT `046a596`; apparatus scripts/relational_formalism_test.py; foundations design/relational_formalism.md).
  Corrected object weights the RELATION as a SCALAR: I_w_rel = sum_{(i,j) in E} w(i,j) I(X_i;X_j) over the DENSE complete graph
  (P3), with I the RAW pairwise MI via CANONICAL cit/information.py at w=ones (clean Shannon boundary), w INDUCED from
  marginal-relative proxies (beta=4.0; the same formal/induced split single-source CIT uses); C_rel = I_w_rel/sum I in [0,1];
  node-induced c_i with the EXACT HANDSHAKE sum_i c_i = 2 I_w_rel closing the overlap. RESULT = GAP CLOSED both families:
  stress-test S1-S6 PASS (S1 REAL Shannon recovery via canonical + non-trivial weight response 4878-7498 bits off-boundary; S2
  non-collapse alpha=w*I ~ 0 at independence, alpha/beta ~ 0.001, vs the retracted merged-node beta=H(X_i,X_j) 1.3-2.0 bits; S3
  handshake exact <=7e-12 at three weight fields; S4 monotonicity; S5 boundedness; S6 within-Dayhoff relabel-invariance; all
  tested at w != 1). The two step-2 FOLLOW-UPS are DISCHARGED (441-vs-21 convention MOOT -- scalar edge weight now; I via
  canonical; overlap closed by the handshake). S7/S8 EVIDENCE (Benjamin rules, NOT decided here): raw-I base favored (sum MIp
  NEGATIVE, ~60% edges MIp<0 -> MIp base leaves [0,1]) + sum-I normalizer favored (C_rel 0.57/0.59 in [0,1]); c1/c3/c-merge
  OPEN. STEP 4-6 (R1-edge = the PRIMARY signature, then its null): c3/c1 RULED (step 4: BASE = raw I [base/weight separation, P7];
  NORMALIZER = sum I; c-merge DEFERRED; beyond-background MIp / max(MIp,0) [c3-gamma] RETRACTED). R1-EDGE (does induced edge-w predict
  PHYLOGENY-CORRECTED coupling PERSISTENCE = median raw MI across K=8 phylo-independent subclades): PILOT PASS on PF13354/PF00026 +
  the clean-tree THIRD family PF00348 (8a7c:A @1.2A, K_eff=6 BALANCED; deterministic outcome-independent selection, 27 skips
  recorded, scripts/select_third_family.py); long-range SEPARATED partial(w, persistence | cons_i,cons_j,bur_i,bur_j) > 0 with
  position-block CI excluding 0, conservation-CLEAN on the K_MI arm. Apparatus scripts/r1_edge.py + r1_edge_family3.py; adversarially
  verified (3x). STEP-6 NARROWINGS: (i) sigma-induction is a RANK NO-OP -> the signatures test the ESTIMATOR not the weight
  magnitudes (the I_w_rel/C_rel functional stays empirically untested); (ii) an advisor 'K_comp~=MIp redundant' premise was FALSE
  (K_comp retains +0.43/+0.26/+0.40 beyond APC-MIp, +0.34/+0.18/+0.39 beyond RAW MI) -> RETRACTED. APPARATUS FIX: pinv->OLS-residual
  in partial_sep/partial_multi (the step-5 '+0.903 cons-null leak' was a pinv-under-collinearity artifact -> ~0). **NULL-PROBE RESULT
  (the decisive within-domain test, adversarially verified 4-agent): K_comp's beyond-raw-MI persistence signal is a MARGINAL-BIAS
  ARTIFACT (FALSIFIED) on ALL 3 families** -- a structured-noise surrogate (destroys within-subclade coupling, preserves
  marginals + subclade phylogeny) reproduces/exceeds the real partial (REAL +0.34/+0.18/+0.39 vs surrogate +0.27/+0.22/+0.46,
  z +6.3/-7.3/-11.7). MECHANISM: K_comp ~= raw MI (Spearman +0.99) -- NOT a distinct paradigm; the 'beyond-MI residual' is degenerate
  noise + shared finite-sample marginal bias. **STEP 7 = D2 RELATIONAL LINE CLOSED AS A FALSIFICATION (2-agent adversarial verify:
  bit-exact from-scratch reimplementation + adversarial break-search; both confirm).** (1) THEOREM: K_comp = N_eff*(raw MI) - KT_penalty,
  an EXACT algebraic identity (verified <=7e-12; OLS R^2 0.987-0.994, slope/N_eff 1.02-1.06, Spearman +0.99) -> K_comp is NOT a distinct
  estimator. The briefed '-200*log2 N' penalty is the right SHAPE but ~3x too large (it assumes the 440-df asymptote; the 441-cell joint is
  ~62% EMPTY, so the offset is occupancy-set ~-720 bits -- CORRECTED against data, not transcribed). (2) RE-RETRACT step-6 narrowing-(ii):
  the 'K_comp genuinely DISTINCT' reading is ITSELF wrong -- the '+0.43 beyond APC-MIp' was JUST the APC background (K_comp~=rawMI;
  APC-MIp=rawMI-background), the '+0.34 beyond RAW MI' was the marginal-bias artifact; BOTH step-6 framings (redundant AND distinct) are
  superseded -> ONE Shannon-plug-in family. (3) R2-edge convergence ILLUSORY: headline Spearman(K_MI,K_comp) +0.54/+0.74 = Spearman(rawMI,
  rawMI-APC); residual after removing raw MI from BOTH arms is NEGATIVE -0.15/-0.45 -> no second paradigm underneath. (4) P4 ('compression
  distinct from information') UNSUPPORTED in D2 (the MDL edge proxy collapses to MI for a fixed finite alphabet; may hold for D1's
  non-analytic zstd/LZ, but untested by an MI-independent estimator in D2). ARC LEDGER -- FALSIFIED/illusory: R2-edge convergence,
  K_comp-as-distinct, P4-in-D2, any coherence-beyond-MI in proteins. SURVIVES: the relational FORMALISM (admissible, a T2 result -- but
  sigma-induction is a rank no-op so the I_w_rel/C_rel weight MAGNITUDES stay UNTESTED); the node-w falsification; M5 standard-MI->contact
  AUROC ~0.80; R1 deflated ('MIp coevolution replicates across phylo-independent subclades, conservation-clean' = the FIELD's standard MI
  signal re-described, NOT compression-specific). NET: D2 recovered the field's pairwise-MI coevolution construct and NOTHING beyond it --
  a clean 'vulnerable in the right way' FALSIFICATION; the WITHIN-DOMAIN protein program is EXHAUSTED as a coherence test. The non-circular
  claim (metacoherence = a TRANSMISSIBLE pattern across DISJOINT-prior domains, a property of the MAP between datasets) is untouched and is
  the next test: CROSS-DISJOINT-DOMAIN TRANSFER with a structured-noise null, NOT another within-domain proxy (K_pred WRONG -- within one
  domain everything collapses to MIp + shared bias). **v0.7.2 D2 relational line CLOSED; v0.7.3 OPENED = cross-domain transfer DESIGN DRAFT
  (design/cross_domain_transfer.md; OPEN -- architecture / domain-pair / 'what counts as transmit' / the multi-scale dependency all pending
  Benjamin + advisor; NO build, NO data, NO lock).** apparatus scripts/r1_null_probe.py. The D2 KxA grid / family-lock / M5-R2 runs stay HELD.
  Then D3 (FOMC), R3, M5 + capstone. (Spec Section 8.7; foundations design/relational_edge_w.md + relational_formalism.md + cross_domain_transfer.md.)
- Tests: 272 fast + 100 slow + 18 very_slow = 390 (1 xfail). v0.7.1: 11 R1-persistence. v0.7.0: 13 D1-structure
  + 35 categorical-proxy + 8 categorical-ablation + 8 R2/cross-tab + 6 crossing-proxy (+1 slow) + 20 decoupling-control (+1 slow).
  v0.6.2: 12 empirics. v0.6.1: 23 coder. v0.6.0: 32 capacity.
  v0.5.5: noise-only counterfactual
  falsifiability (each off-diagonal pair structured >= 0.5 AND noise < 0.3, `T_NOISE=0.3`);
  33 new noise tests on A1+A3 (all 15 pairs) + A2 sample. Seam 1 resolved `(K5, K2)`-specific.

## Locked constants (pre-registered — do NOT change without a version bump + amendment)

- `beta = 4.0` — weight-map sensitivity, locked from v0.2. In `cit/induce.py` and
  `cit/induce_multi.py:BETA`.
- `NEURAL_SEED = 7` — K3 GRU init/SGD. CPU-only; `torch.use_deterministic_algorithms(True)`.
- `HMM_SEED = 0` — K4 Baum-Welch EM init. CPU/numpy deterministic. In `cit/proxies/mdl_hmm.py`.
- `DEFAULT_CORRELATION_THRESHOLD = 0.15` — A3 clustering, `cit/ablations/correlation_cluster.py`.
- `SEED = 42` — Shannon-recovery stochastic tests, `tests/test_shannon_recovery.py:SEED`.
- `STREAM_SEED = 42` — synthetic-stream generation. In `tests/test_induction_pipeline.py`,
  `test_cross_proxy_validation.py`, `test_cross_ablation_validation.py`, `test_multi_feature_substrate.py`.
- `ABLATION_SEED = 123` — ablation RNG (A1 LOO / A2 Shapley / A3 corr-cluster). Same four test files.
- Convergence thresholds: cross-proxy Spearman rho >= 0.5 (multi-feature substrate);
  cross-ablation rho >= 0.7 (A1 vs A2) plus per-symbol sign agreement.
- Collapse tolerances: algebraic identity `1e-12`; empirical convergence per-distribution
  atol in `pre_registration.md`.
- Capacity solver (v0.6.0): `tol = 1e-10`, `max_iter = 2000`, `lattice_m = 20`, no RNG
  (deterministic, bit-exact). In `cit/capacity.py`. Closed-form-anchor test atol `1e-8`
  (corrected from 1e-9 post-impl; the locked tol floors at ~1e-9 on the flat eps=0 max).
- Selective coder (v0.6.1): `ZSTD_LEVEL = 19`; achievability test atol `0.02` bits/sym at `N=200_000`.
  In `cit/coders/selective.py`. v0.6.2 win-margin: `WIN_MARGIN = 0.20`, `N=100_000`, seeded substrates.
- v0.7.0 categorical (`cit/proxies/categorical.py`, `cit/ablations/categorical.py`, `cit/metacoherence.py`):
  `SHUFFLE_SEED = 0` (K1/K5 time-shuffle surrogate baseline); K1 `_ZSTD_LEVEL_K1 = 3`; feature-major bit-tight
  encoding (`ceil(log2 A)` bits/feature, channel-grouped -- the post-audit correctness fix, do NOT revert
  to step-major); `GRID_ABLATION_SEED = 123`; K3 `NEURAL_SEED=7`, K4 `HMM_SEED=0` carried. R2 threshold
  `0.6` / CI `0.4` KEPT (number unchanged) but RECLASSIFIED by the bbd081c reframe: a CONVERGENCE FLAG,
  NOT a pass/fail gate -- R2 is DIAGNOSTIC (corroborating on convergence, non-falsifying on divergence,
  coverage-capped); falsifiability relocated to R1/R3 (pre-reg 2026-06-24 program reframe).
- v0.7.0 decoupling control (`cit/metacoherence.py`): `DECOUPLE_STABILITY_N = 18` (per-proxy sign-count
  supermajority of `N_REPLICATES=20`); `DECOUPLE_CONFIDENT = 0.40` / `DECOUPLE_WEAK = 0.10` (|median Delta|
  two-band magnitude); `CROSSING_REFS` (twin-excluded nine-cell refs for K3b/K2b); `DECOUPLE_PROXIES =
  PROXIES + (K3b, K2b)`. Crossings carry `NEURAL_SEED=7` (K3b) + `SHUFFLE_SEED=0`. NO locked constant VALUE
  was changed by ANY v0.7 work.
- D1 substrate (v0.7.0, pre-registered; BUILT): 3-state HSMM, mean dwell 200, dispersion
  `r=6`, `T=50_000`, `N_REPLICATES=20`; 8 alphabet-8 features (`F0_scale=1.7`; B lag `L=12`,
  `B_keep=0.35`; C additive mask; D drift `std=0.10`, `peak=1.0`); M5 partition coherence-bearing
  {f0..f4} / noise {f5..f7}. R2 threshold median Spearman `> 0.6` (CI `> 0.4`); bootstrap `B=1000`
  (block = mean sojourn 200). MARGINAL-RELATIVE coherence is a hard requirement. `cit/data/hsmm_d1.py`
  (pending). Calibrated by MI-balancing (Sec 5.4); exact K3xA1 ceiling verified in-build.

The locked record is `pre_registration.md`. If evidence forces a change: bump the
version, record the amendment in that file's history section, never silently edit.

## Open seam (do not "fix" silently)

Seam 1: `(K5, K2)` under A2 Shapley sits at Spearman 0.491, just under the 0.5
threshold. **Resolved at v0.5.5 as `(K5, K2)`-specific** — of all `(X, K2)` pairs under
A2 only K5 misses; K3, K4 (0.830), form B, K1 all clear — so the framework's operating
envelope is not restricted. It stays mechanically `xfail(strict=True)` as a documented
near-miss; leave it xfail (a strict XPASS forces re-evaluation) unless Benjamin directs otherwise.

## Test gating

- Default `pytest` runs fast only (`addopts = -m 'not slow and not very_slow'`).
- `slow` (~5-10 min): LOO + CorrCluster K5 + proxy invariants. Run with `-m slow`.
- `very_slow` (Shapley K5, ~135 min): `workflow_dispatch` only. Run with `-m very_slow`.
- K3 Shapley (A2) is ~4.3h/fixture, local-gated (exceeds 6h hosted ceiling). Hosted
  very_slow runs K5 family only via `-k "not K3"`.

## Working conventions (§8)

- One sub-step per "proceed." Hand steering back; no unsupervised bulk output.
- Surgical Python edits via `python << 'PYEOF'` with BOTH guards:
  `assert src.count(old) == 1` (anchor) AND `assert <distinctive-new-token> not in src`
  (idempotency — the anchor alone misses double-application after a clean first run).
- Heredocs use `MULTIEOF`, not `EOF`.
- ASCII-only in code payloads. Unicode allowed in README.md and pre_registration.md prose.
- Commits: two `-m` flags, dense paragraph body. Version strings `"vX.Y.Z: subject"`.
- Parse at the bit level, not byte level, where byte-level clips a metric to zero.
- Pre-register before implementation; if structural findings emerge, pre-register
  honestly rather than silently adjusting thresholds.

## Environment

- Python 3.11 / 3.12. `python3.12 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`.
- Deps: numpy<2, zstandard, numba>=0.60, torch>=2.0,<2.3.
- x86 <-> arm64 migration breaks bit-exact CI parity; treat as a multi-day
  measurement-and-amendment lift, not a quick port.

## Roadmap (next)

v0.6 program COMPLETE. v0.7 cross-domain (Metacoherence) IN PROGRESS, all committed on main through
`bbd081c`: v0.7.0 D1 build (`d9eb3b5`, `823928a`) + record-correction (`f1d1da3`, instrument-validity not
falsification) + decoupling control (pre-reg `7cca0c5`, proxies `231fd94`, metric `8277bdb`, wiring
`3ea5c50`, RESULT `d840553`) + program reframe (`bbd081c`). The decoupling control RAN -> verdict
INCONCLUSIVE / necessary-not-sufficient: K3b modeling-confident (20/20, median +0.51), K2b unstable
(17/20); a read-only I_C diagnostic REJECTED property-dependence, so K2b's near-miss is genuine NOISE;
(e)(i) hold-encoding-constant stays gated/unjudged. PROGRAM REFRAME (epistemics): D1 recast as ESTIMATOR
COVERAGE-CALIBRATION (DIFFERENTIAL coverage, K5/parsing MOST COMPLETE, ASYMMETRIC not compositional); R2
reclassified DIAGNOSTIC (0.6/0.4 kept as a convergence flag, non-falsifying on divergence); R1 (persistence)
+ the v0.6.2 selective-compression functional win ELEVATED to PRIMARY (per-estimator functional validity
AGGREGATED, NOT cross-estimator prediction-agreement -- the R1 spec guard). Eight-cell matrix needs
RE-DERIVATION under R2-as-diagnostic (capstone-pending). v0.7.1 R1 BUILT + RUN + CLOSED (`90a3211` pre-reg ->
`346f700` build-time amendment -> `95d85ff` apparatus+finding -> `7963eb5` closer): D1 R1 = CALIBRATION,
necessary-not-sufficient AND MECHANISM-CONFOUNDED; cost ordering D-LED (information-sensitive within property,
concentration-biased across, 20-seed disambiguation); partial proxy d-matrix K1 FAILS / K2 PASSES; concentration
confound parked for D2/D3 (emission-concentration-homogeneity check pre-registered first); the full R1 grid
(K3/K4/K5, A2) deferred (predictable/confounded/slow). D2 (Pfam, CC0) R1 PRE-REGISTERED (`df025a3`; ML
per-site-rate substitution tolerance + conservation-tautology confound check). D2 advanced through survey +
rework/resolution/redesign + a framing-S premise check (proxies EMPTY) + a coupling pilot (INTERMEDIATE: pairwise
coevolution real + conservation-independent, per-position projection weak); check B' RAN + FAILED (no edge->node
node-aggregation beats burial-controlled conservation -> the edge->node projection loses the signal). B2 (graph-structural
node projections) RAN + PASSED NARROWLY (g_pr/PageRank partial +0.151 > conservation +0.143; g_eig/g_topL fail; thin +0.008,
single family, prediction inverted) -> Sec 6.2 NODE-VALUED w SURVIVES (edge-valued branch A NOT forced). SECOND-FAMILY
replication + EDGE-M5 RAN (PF00026 Asp / 4y9w:A; L=312; apparatus scripts/run_d2_family2.py; matrix recipe BIT-EXACT to
PF13354): RESULT = EDGE GENERALIZES (check A 0.160 vs base 0.019; edge-M5 PASS, MIp-AUROC 0.802 > cons-prod 0.442 AND >
burial-prod 0.685, long 0.794 > 0.700) but NODE does NOT clear the HARDENED bar (g_pr partial +0.127 vs phylo-cons +0.134,
margin -0.007 CI includes 0; B2 g_pr pass did NOT replicate; winning projection unstable g_pr/g_topL). PF13354 edge-M5
fold-in: MIp 0.698 beats conservation but LOSES to burial 0.716 -> the edge-vs-burial margin is family-dependent. MIXED vs
the strict rules ('node-fail generalizes' not literally met because B' beat the weaker entropy ref; hardened phylo bar
fails) -> BRANCH ADJUDICATED (Benjamin): node-valued w RETIRED, EDGE-valued w ADOPTED (corpus-aligned dense coupling field).
RELATIONAL BUILD step 1 RAN + PASSED (apparatus scripts/r2_edge.py): R2-EDGE premise = convergence of K_MI (APC-MIp) vs
K_comp (MDL/KT compression edge coupling), DCA EXCLUDED as Pearlian -> R2-EDGE PASS BOTH families (long-range Spearman +0.542
PF13354 / +0.745 PF00026 >=0.5; consensus-edge contact precision beats each alone; convergence STRENGTHENS under
conservation/burial control, partial +0.651/+0.852). Caveat top-L Jaccard modest (0.15/0.24); two families, no grid, no lock.
Edge-valued direction supported by cross-paradigm convergence. RELATIONAL BUILD step 2 = edge-w FORMAL-ADMISSIBILITY check
RAN + PASSED-AS-CODED but RETRACTED by step 3 (it verified the WRONG object -- edge-w = CIT per-symbol w on the 441-joint
pair-symbol, which COLLAPSES to single-source node-w, weights joint VALUES not the RELATION, fails canonical I_w's 21-symbol
shape -- AND the PASS was TAUTOLOGICAL: check B hardcoded np.ones, the pair-OVERLAP risk was never probed). RELATIONAL BUILD
step 3 = RETRACT that object + the step-2 PASS + INSTALL the corrected RELATIONAL functional + stress-test (pre-reg `017a7e4`
-> RESULT `046a596`; apparatus scripts/relational_formalism_test.py; foundations design/relational_formalism.md). Corrected
object weights the RELATION as a SCALAR: I_w_rel = sum_{(i,j) in E} w(i,j) I(X_i;X_j) over the DENSE complete graph (P3), I =
RAW pairwise MI via CANONICAL cit/information.py at w=ones (clean Shannon boundary), w INDUCED from marginal-relative proxies
(beta=4.0; same formal/induced split as single-source CIT); C_rel = I_w_rel/sum I in [0,1]; node-induced c_i with the EXACT
HANDSHAKE sum_i c_i = 2 I_w_rel closing the overlap. RESULT = GAP CLOSED both families (S1-S6 PASS: S1 REAL Shannon recovery
via canonical + non-trivial weight response; S2 non-collapse alpha~0 at independence vs merged-node beta large; S3 handshake
exact <=7e-12; S4 monotonicity; S5 boundedness; S6 within-Dayhoff relabel-invariance; tested at w != 1). The two step-2
follow-ups are DISCHARGED (441-vs-21 convention MOOT -- scalar edge weight; I via canonical; overlap closed by the handshake).
S7/S8 EVIDENCE (Benjamin rules): raw-I base favored (sum MIp NEGATIVE, ~60% edges MIp<0) + sum-I normalizer favored (C_rel
0.57/0.59 in [0,1]). c1/c3 RULED (raw-I base + sum-I; c-merge deferred). R1-EDGE = PRIMARY signature: PILOT PASS on 3 families incl.
the clean-tree PF00348 (conservation-clean K_MI arm). STEP-6 NULL-PROBE (adversarially verified) FALSIFIED K_comp's beyond-raw-MI
persistence as a MARGINAL-BIAS ARTIFACT (all 3 families). STEP 7 = D2 RELATIONAL LINE CLOSED AS A FALSIFICATION (2-agent adversarial verify:
bit-exact reimplementation + break-search): THEOREM K_comp = N_eff*(raw MI) - KT_penalty, an EXACT identity (<=7e-12; R^2 0.987-0.994,
slope/N_eff ~1.0-1.06, Spearman +0.99) -> K_comp NOT a distinct estimator (the briefed -200*log2 N penalty is occupancy-set ~-720, CORRECTED
against data); narrowing-(ii) RE-RETRACTED (the 'K_comp distinct' reading was JUST the APC background; ONE Shannon-plug-in family); R2-edge
convergence ILLUSORY (headline = Spearman(rawMI, rawMI-APC); residual after removing raw MI from BOTH arms NEGATIVE -0.15/-0.45 -> no second
paradigm); P4 ('compression distinct from information') UNSUPPORTED in D2 (the MDL edge proxy collapses to MI for fixed finite alphabet; may
hold for D1's non-analytic zstd/LZ). ARC LEDGER -- FALSIFIED/illusory: R2-edge convergence, K_comp-as-distinct, P4-in-D2, any
coherence-beyond-MI in proteins; SURVIVES: the relational FORMALISM (admissible T2 -- weight MAGNITUDES untested, sigma-induction a rank
no-op), the node-w falsification, M5 standard-MI->contact AUROC ~0.80, the deflated R1 (the field's standard subclade-replicated MI
coevolution, conservation-clean). NET: D2 recovered the field's pairwise-MI coevolution construct and NOTHING beyond it -- the WITHIN-DOMAIN
protein program is EXHAUSTED. The decisive test is CROSS-DISJOINT-DOMAIN TRANSFER with a structured-noise null, NOT another within-domain
proxy. **v0.7.2 D2 relational line CLOSED; v0.7.3 OPENED = cross-domain transfer DESIGN DRAFT (design/cross_domain_transfer.md; OPEN --
architecture / domain-pair / 'what counts as transmit' / multi-scale dependency pending Benjamin + advisor; NO build/data/lock).** D2
grid/family-lock/M5-R2 runs HELD; then D3 (FOMC), R3, M5 + capstone. Deferred
(not pre-judged): the full R1 grid; the A2-Shapley rescue verdict; the
R2-statistic all-pairs-vs-cross-philosophy-pairs decision.
