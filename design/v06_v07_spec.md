# CIT Architecture & Design Spec -- v0.6-v0.7 reference

**Status:** living design reference. Current through HEAD = `3042fe2` (2026-06-24; D2 beta-line): the v0.5
robustness program and the v0.6 operational-theorem program are SHIPPED; v0.7.0 (cross-domain D1)
is BUILT + record-corrected, the DECOUPLING CONTROL is BUILT + RUN, the v0.7 PROGRAM has been
REFRAMED, **v0.7.1 R1 (persistence) is BUILT + RUN + CLOSED** (as calibration; Section 8.5), and
**D2 (Pfam) R1 is PRE-REGISTERED** (Section 8.6). The decoupling control (modeling-on-byte-stream crossings K3b/K2b, A1, full-T, 20 seeds)
returned verdict INCONCLUSIVE / necessary-not-sufficient: K3b modeling-confident (n_M 20/20, median
Delta +0.506), K2b unstable (17/20, one seed short of 18/20); a pre-registered read-only I_C diagnostic
REJECTED a property-dependent-representation explanation, so K2b's near-miss is genuine NOISE; control
(e)(i) stays gated/unjudged (Section 8.3). The v0.7 PROGRAM REFRAME (epistemics, not results; Section 8.4):
D1's role is recast from R2-pass/fail to ESTIMATOR COVERAGE-CALIBRATION vs known ground truth (finding:
DIFFERENTIAL coverage with K5/parsing MOST COMPLETE, ASYMMETRIC not compositional); R2 is reclassified
DIAGNOSTIC (corroborating on convergence, NON-FALSIFYING on divergence -- the 0.6/0.4 numbers are KEPT as
a convergence flag, not a gate); R1 (persistence) + the v0.6.2 selective-compression functional win are
ELEVATED to PRIMARY cross-domain evidence (falsifiability RELOCATED to R1/R3). **v0.7.1 R1 RESULT (Section 8.5):**
a read-only re-read of the locked D1 generator found its regime path is EMISSION-INDEPENDENT (the Sec 5.4
drift->transition coupling is NOT instantiated), so D1 R1 = INSTRUMENT-CALIBRATION, necessary-not-sufficient
AND MECHANISM-CONFOUNDED; the decoder-free log-likelihood-cost magnitude is D-LED (a 20-seed diagnostic
disambiguates it as information-sensitive WITHIN a property + concentration-biased ACROSS), and a partial proxy
d-matrix confirms K1 FAILS / K2 PASSES; the concentration confound is parked for D2/D3 behind a pre-registered
emission-concentration-HOMOGENEITY check. **D2 (Pfam) R1 PRE-REGISTERED (Section 8.6):** ML per-site-rate
substitution tolerance + the conservation-tautology confound check (entropy-baseline contrast). See
`pre_registration.md` (2026-06-23 / 2026-06-24 amendments) for the authoritative record. Version 0.7.1 (the v0.7 line -- D1 + decoupling + reframe + R1 calibration + the D2 pre-registration -- shipped + tagged `v0.7.1` 2026-06-24). v0.7.2 (D2 relational line) CLOSED 2026-06-25 as a FALSIFICATION (unreleased); v0.7.3 OPENED = cross-domain transfer DESIGN DRAFT: the D2 beta-line (Section 8.7) advanced through survey + framing-S-EMPTY + coupling-pilot-INTERMEDIATE + B'-FAIL + B2-PASS (narrow) + the SECOND-FAMILY replication (PF00026): EDGE GENERALIZES (edge-M5 MIp-AUROC 0.80 beats conservation AND burial, even long-range) but the NODE-valued w does NOT clear the phylo-hardened bar (B2 g_pr pass did NOT replicate; margin vs phylo -0.007, CI includes 0) -> edge de-risked, node not; BRANCH ADJUDICATED (Benjamin): node-valued w RETIRED, EDGE-valued w ADOPTED (corpus-aligned dense coupling field). RELATIONAL BUILD step 1 (R2-EDGE premise) RAN + PASSED both families: K_MI (APC-MIp) vs K_comp (MDL/KT compression edge coupling, DCA EXCLUDED as Pearlian) converge (long-range Spearman +0.54/+0.75), consensus edges beat each alone on contact precision, and convergence STRENGTHENS under the conservation/burial control (partial +0.65/+0.85). RELATIONAL BUILD step 2 (edge-w FORMAL-ADMISSIBILITY) RAN + PASSED-AS-CODED but RETRACTED by step 3 (it verified the WRONG object -- edge-w = CIT per-symbol w on the 441-joint pair-symbol COLLAPSES to single-source node-w, weights joint VALUES not the RELATION, fails canonical I_w's 21-symbol shape -- and the PASS was TAUTOLOGICAL: check B hardcoded np.ones, the pair-overlap risk never probed). RELATIONAL BUILD step 3 RETRACTED that object + the step-2 PASS, INSTALLED the corrected RELATIONAL functional I_w_rel = sum w(i,j) I(X_i;X_j) over the DENSE complete graph (I = RAW pairwise MI via canonical cit/information.py at w=ones; w INDUCED from marginal-relative proxies; C_rel in [0,1]; exact HANDSHAKE sum_i c_i = 2 I_w_rel closing the overlap), and stress-tested it -> GAP CLOSED both families (S1-S6 PASS; S7/S8 evidence favors raw-I base + sum-I normalizer; c1/c3/c-merge = Benjamin's rulings; the two step-2 follow-ups DISCHARGED). RELATIONAL BUILD steps 4-6: c3/c1 RULED (raw-I base + sum-I; foundation P7 base/weight separation); R1-EDGE (the PRIMARY signature) PILOT-PASSED on 3 families incl. the clean-tree PF00348, but its DECISIVE structured-noise NULL-PROBE FALSIFIED K_comp's beyond-raw-MI persistence as a MARGINAL-BIAS ARTIFACT on ALL 3 (K_comp ~= raw MI, Spearman +0.99 -> NOT a distinct paradigm; refines R2-edge's 'distinct paradigms' framing) -> CONCEDE the beyond-MI finding as within-domain noise; the decisive test is CROSS-DISJOINT-DOMAIN TRANSFER, not another within-domain proxy. SURVIVES = MIp coevolution persists across subclades conservation-clean (the field's standard MI re-described). STEP 7 = D2 RELATIONAL LINE CLOSED AS A FALSIFICATION (2-agent adversarial verify: bit-exact reimplementation + break-search): THEOREM K_comp = N_eff*(raw MI) - KT_penalty, an EXACT identity (<=7e-12; OLS R^2 0.987-0.994, slope/N_eff ~1.0-1.06, Spearman +0.99) -> K_comp NOT a distinct estimator (the briefed -200*log2 N penalty is occupancy-set ~-720 bits -- CORRECTED against data, the 441-cell joint is ~62% empty); narrowing-(ii) RE-RETRACTED (the 'K_comp distinct' reading was JUST the APC background; ONE Shannon-plug-in family); R2-edge convergence ILLUSORY (headline Spearman = Spearman(rawMI, rawMI-APC); residual after removing raw MI from BOTH arms NEGATIVE -0.15/-0.45 -> no second paradigm); P4 ('compression distinct from information') UNSUPPORTED in D2 (the MDL edge proxy collapses to MI for a fixed finite alphabet; may hold for D1's non-analytic zstd/LZ). ARC LEDGER -- FALSIFIED/illusory: R2-edge convergence, K_comp-as-distinct, P4-in-D2, any coherence-beyond-MI in proteins; SURVIVES: the relational FORMALISM (admissible T2 -- weight MAGNITUDES untested), node-w falsification, M5 MI->contact AUROC ~0.80, deflated R1. NET: D2 recovered the field's pairwise-MI coevolution construct and NOTHING beyond it -- the within-domain protein program is EXHAUSTED as a coherence test. v0.7.2 CLOSED; v0.7.3 OPENED = cross-domain transfer DESIGN DRAFT (design/cross_domain_transfer.md; OPEN -- architecture / domain-pair / 'what counts as transmit' / multi-scale dependency pending Benjamin + advisor; NO build, NO data, NO lock).

**WHERE WE ARE (continuation pointer).** Shipped this line: v0.6.0 capacity estimator, v0.6.1
selective coder (Thm 5.1 repaired), v0.6.2 win-margin empirics. v0.7.0 D1 is BUILT + record-corrected;
the decoupling control is BUILT + RUN (verdict INCONCLUSIVE, Section 8.3); the v0.7 program is REFRAMED
(Section 8.4: D1 -> coverage-calibration, R2 -> diagnostic, R1/functional -> PRIMARY). v0.7.1 R1 is now
CLOSED as calibration (Section 8.5; the R1 SPEC GUARD held -- per-estimator functional validity AGGREGATED,
NOT cross-estimator agreement); D2 (Pfam) R1 was PRE-REGISTERED (8.6) then ADVANCED through the beta-line (Section 8.7): the survey RAN, the
framing-S marginal-relative proxies measured EMPTY, a coevolution-coupling pilot is INTERMEDIATE, and the
pre-registered B' check FAILED on naive aggregations, but B2 (graph-structural projections) PASSED NARROWLY via PageRank
(+0.151 vs conservation's +0.143) -- so Sec 6.2's NODE-VALUED w SURVIVES (razor-thin, SINGLE family; the pre-reg rule REQUIRES
replication on >= 1 more coevolution-rich family before any lock; the recorded prediction was INVERTED -- g_topL failed, global
PageRank flow passed). The SECOND-FAMILY replication + edge-M5 then RAN on PF00026 (Asp / 4y9w:A): EDGE GENERALIZES
(edge-M5 MIp-AUROC 0.80 beats both conservation- AND burial-product, even long-range) but the NODE-valued w does NOT clear
the PHYLO-HARDENED bar (PageRank's burial-controlled margin vs phylo-conservation = -0.007, CI includes 0; the B2 pass did
NOT replicate; winning projection unstable) -> edge DE-RISKED, node NOT; node-valued w RETIRED, EDGE-valued w ADOPTED. The
RELATIONAL BUILD step 1 R2-EDGE premise then RAN + PASSED both families (K_MI APC-MIp vs K_comp MDL/KT compression coupling,
DCA excluded as Pearlian; long-range Spearman +0.54/+0.75, consensus edges beat each alone, convergence strengthens under the
conservation/burial control) -> the edge-valued direction is supported by cross-paradigm convergence. RELATIONAL BUILD
step 2 (formal-admissibility) RAN + PASSED-AS-CODED but was RETRACTED by step 3 (a tautological PASS on the WRONG 441-joint
object that collapses to node-w); step 3 RETRACTED that object + the step-2 PASS, INSTALLED the corrected relational functional
I_w_rel (weights the SCALAR edge MI on the dense graph; I via canonical cit/information.py; the exact handshake closes the
overlap), and stress-tested it -> GAP CLOSED both families (S1-S6 PASS; evidence favors raw-I + sum-I; c1/c3/c-merge =
Benjamin's rulings). Steps 4-6 then RULED c3/c1, PILOT-PASSED R1-EDGE on 3 families (incl. the clean-tree PF00348), and FALSIFIED K_comp's beyond-raw-MI persistence as a marginal-bias artifact (K_comp ~= raw MI +0.99). STEP 7 CLOSED the D2 relational line as a FALSIFICATION (2-agent adversarial verify): K_comp = N_eff*(raw MI) - KT_penalty is an EXACT identity -> K_comp NOT a distinct estimator (the briefed -200*log2 N penalty CORRECTED to occupancy-set ~-720); R2-edge convergence ILLUSORY (residual after removing raw MI from both arms NEGATIVE); P4 UNSUPPORTED in D2. NET: D2 recovered the field's pairwise-MI coevolution construct and nothing beyond it -- the within-domain protein program is EXHAUSTED; the decisive test is CROSS-DISJOINT-DOMAIN TRANSFER. v0.7.2 CLOSED; v0.7.3 OPENED = cross-domain transfer DESIGN DRAFT (design/cross_domain_transfer.md; OPEN -- pending Benjamin + advisor). NEXT relational component = Benjamin's call (cross-domain transfer / D3). The D2 grid / family-lock / M5 runs stay HELD. Then D3 (FOMC); v0.7.2 R3; the M5 +
eight-cell capstone (the eight-cell matrix needs RE-DERIVATION under R2-as-diagnostic). Three
SOURCE-PAPER soundness findings recorded this program (the framework being "vulnerable in the right
way"): the Sec 6 capacity-fixture erratum (v0.6.0); the Thm 5.1 selective-compression unsoundness for
w!=1 (v0.6.1, repaired to the merged-source floor H(Z)); and the R2-as-cross-extractor-convergence
metrology analogy failing under the coverage ceiling (v0.7 reframe, R2 demoted to diagnostic). Boot
procedure: read this file + `pre_registration.md` (authoritative).

**Scope:** the architecture through v0.6 (shipped) plus the v0.7 cross-domain design + the D1 build plan.

**Authority.** This document is a DESIGN/ARCHITECTURE reference, not a locked record.
The authority order is: **Benjamin live > global ACRE > `pre_registration.md` (the locked
commitments, authoritative over code) > this spec > code comments.** Anything described
here as "planned" / "proposed" / "open choice" for v0.6-v0.7 is NOT yet pre-registered;
it becomes binding only when written into `pre_registration.md` as a dated amendment
BEFORE implementation. If this spec and `pre_registration.md` ever disagree, the pre-reg wins.

---

## 0. Orientation -- how to use this doc

CIT (Coherence Information Theory) is the empirical, falsifiable arm of the Recursive
Coherence corpus. The repo's reason for existing: **commitments must precede outcomes.**
Every estimator/threshold is pre-registered before it is run, so the framework is
"vulnerable in the right way." A passing test suite that no longer tests convergence is
lock-in, not success.

Sections 1-6 describe what exists and the working method. Section 7 (v0.6 operational theorems) is
now BUILT and shipped (capacity / selective coder / win-margin). Section 8 (v0.7 cross-domain) holds
the D1 build (8.1, COMPLETE -- retained for reference), D1 lessons + risks (8.2), the decoupling-control
RESULT (8.3), the v0.7 PROGRAM REFRAME (8.4), the v0.7.1 R1 RESULT (8.5), and the D2 R1 PRE-REGISTRATION (8.6).
The ACTIVE FRONTIER is now the D2 (Pfam) build -- the load-bearing R1 domain -- gated on the data survey; R1
is CLOSED on D1 as calibration, with R2 running as a diagnostic. Sections 9-10 are the M-conditions
and source documents; 11-12 are open issues and notation.

---

## 1. Thesis and formal foundation

CIT generalizes Shannon by attaching a bounded **coherence weight** `w(x) in [0,1]`
(the papers write `kappa(x)`; `w == kappa` throughout) to each source symbol, measuring
that symbol's contribution to recursive structural stability. Three core quantities
(implemented in `cit/information.py`, all default to bits / base-2):

    H(X)      = -sum_x p(x) log p(x)                          (Shannon entropy)
    H_w(X)    = sum_x p(x) w(x) [-log p(x)]                   (coherence-weighted entropy)
    I_w(X;Y)  = sum_{x,y} p(x,y) w(x) log[p(x,y)/(p(x)p(y))]  (coherence-weighted MI)
              = E_{p(x) w(X)} D( p(Y|X) || p(Y) )

**Boundary condition (the spine).** When `w(x) = 1` for all x, every weighted quantity
collapses EXACTLY to its Shannon counterpart. This is what licenses CIT as a
*generalization*, not a replacement. Enforced empirically by `tests/test_shannon_recovery.py`.
Every future estimator, ablation, weight map, OR CODER must preserve this collapse.

**Proved properties of `I_w`** (from the formal paper, see Section 7.1):
- P1 nonnegativity: `I_w >= 0` (since `D >= 0`, `w >= 0`); `=0` iff `p(y|x)=p(y)` for all x with `w(x)>0`.
- P2 upper bound: `0 <= I_w(X;Y) <= I(X;Y)` (weighting never increases MI, since `w <= 1`).
- P3 asymmetry: `I_w(X;Y) != I_w(Y;X)` in general (weights attach to X).
- Weighted Data Processing Inequality: `X->Y->Z` Markov under same `w` => `I_w(X;Z) <= I_w(X;Y)`.

`H_w == H_kappa`: the paper's `H_kappa = -sum kappa(x) p(x) log p(x)` and the repo's
`H_w = sum p(x) w(x) [-log p(x)]` are algebraically identical (the weight multiplies the
surprisal). State this equivalence anywhere the H_w bound is used.

---

## 2. The claim under test (the falsifiable core)

The whole construct rests on ONE empirical claim, now established through v0.5.5:

> Independent proxies of "coherence" (different epistemic bases: prediction, compression,
> MDL, neural, parsing) and independent ablation operators (LOO, Shapley, correlation-cluster)
> CONVERGE on the same per-symbol coherence signal `rho(x)` on structured data, and that
> convergence is DESTROYED on a structure-free (noise-only) counterfactual.

If independent proxies did not converge, the construct would be empty (no stable thing
being measured). If they converged even on noise, the construct would be circular (an
artifact of the method). v0.5 demonstrated neither failure mode occurs. v0.6-v0.7 build
the operational and cross-domain theory ON TOP of this validated signal.

---

## 3. Repository architecture (current = v0.7, HEAD `3042fe2`)

### 3.1 Pipeline (the spine of the induced-weight path)

    stream  --proxy K-->  C_hat (scalar coherence)
            --ablation A-->  rho(x) (per-symbol/feature contribution, centered)
            --sigmoid-->     w(x) = sigma(beta * rho(x)),  beta = 4.0 (locked)

Proxies and ablations are deliberately swappable; the convergence claim IS that the
choice of K and A does not change the rho signal's structure.

### 3.2 Module map

| Layer | Module | Role |
|-------|--------|------|
| Formal | `cit/information.py` | `H`, `H_w`, `I_w` (+ aliases `shannon_entropy`, `coherence_weighted_entropy`, `coherence_weighted_mutual_information`), `pmf_from_counts`. base-2 default; weights validated to [0,1]; probs validated to simplex. |
| Substrate (1-D) | `cit/data/synthetic.py` | `labeled_coherence_stream` -- single-symbol sticky-Markov coherent symbols + i.i.d. noise (v0.2 substrate). |
| Substrate (multi) | `cit/data/multi_feature.py` | `labeled_multi_feature_stream` (shared 2-state HMM, 4 coherent + 6 noise binary features, marginal-matched) and `noise_only_multi_feature_stream` (all i.i.d. Bernoulli(0.5)). The v0.5 substrate. |
| Proxies (1-D) | `cit/proxies/predictive_logloss.py`, `compression_delta.py` | form B (predictive log-loss), K1 (zstd compression-delta). |
| Proxies (multi) | `predictive_logloss_multi.py`, `compression_delta_multi.py`, `ngram_mdl.py`, `lempel_parsing.py`, `neural_prequential.py`, `mdl_hmm.py` | form B multi, K1 multi, K2, K5, K3, K4 (see 3.4). |
| Ablations (1-D) | `cit/ablations/loo.py`, `shapley.py` | A1 LOO, A2 Shapley (single-symbol). |
| Ablations (multi) | `loo_multi.py`, `shapley_multi.py`, `correlation_cluster.py` | A1, A2, A3 (feature-level). |
| Induction | `cit/induce.py`, `cit/induce_multi.py` | `induce_weights` (1-D), `induce_weights_multi` (multi). `BETA = 4.0`. |
| Coders | `cit/coders/selective.py` | v0.6.1 selective compression coder (corrected `H(Z)` theorem; Section 7.3). |
| Substrate (v0.7 D1) | `cit/data/hsmm_d1.py` | the D1 cross-domain substrate: 3-state HSMM, 8 alphabet-8 features (4 properties A/B/C/D + 3 distractors), seeds 7000..7019. |
| Proxies (v0.7 categorical) | `cit/proxies/categorical.py` | categorical (alphabet-A) marginal-relative K1-K5 (feature-major bit-tight encoder; time-shuffle surrogate baseline for K1/K5). |
| Proxies (v0.7 crossings) | `cit/proxies/crossing.py` | decoupling-control crossings K3b (`neural_prequential_byte_proxy`) + K2b (`bigram_mdl_byte_proxy`): the K3/K2 modeling functionals re-serialized onto the byte stream (Section 3.8). |
| Ablations (v0.7 categorical) | `cit/ablations/categorical.py` | A1/A2/A3 categorical (uniform-over-alphabet replacement). |
| Induction (v0.7) | `cit/induce_cat.py` | `induce_weights_cat` (threads the alphabet to proxy + ablation). |
| Metacoherence (v0.7) | `cit/metacoherence.py` | the 5x3 R2 grid + property-recovery cross-tab + `partition_diagnostic`; AND the decoupling metric (Section 3.8): `crossing_delta`, twin-excluded nine-cell `concordance_verdict`, `decoupling_control_verdict`, `compute_decoupling_run`, `DECOUPLE_*` constants. |
| Persistence (v0.7.1 R1) | `cit/persistence_d1.py` | the D1 R1 apparatus (Section 8.5): additive sibling generator `stream_with_emission_dists` (re-runs the locked generation BIT-EXACT + exposes the per-step emission distributions), `generate_perturbed_stream` (RNG-preserving single-feature corruption), the decoder-free `persistence_cost_table` (sustained marginal-relative log-likelihood-cost magnitude), numpy `cohens_d` + B=1000 bootstrap, `validation_gate`, `compute_r1_run`. Locked `generate_stream` untouched. |
| Run drivers (v0.7) | `scripts/run_metacoherence_grid.py`, `scripts/run_decoupling_control.py` | the R2-grid CI job + the 20-seed decoupling-control run driver. (v0.7.1 R1 cheap grid ran inline; no driver written.) |
| Artifact (v0.7) | `results/decoupling_control/` | committed `verdict.json` + 20 `seed_*.json` + run scripts (`results/.gitignore` excludes transient logs/errs/tmps). |
| Artifact (v0.7.1) | `results/r1_persistence/` | `cost_table_T50000.json` (the estimator-agnostic 20-seed cost table, reused) + `d_matrix_cheap.json` (the partial proxy d-matrix: K1 FAILS / K2 PASSES). |
| Tests | `tests/test_*.py` | 15 files (see 3.7). |
| Design | `design/multi_feature_substrate.md`, `design/v06_v07_spec.md` (this file) | locked v0.5 substrate memo + this spec. |

### 3.3 The contracts (stable interfaces v0.6 must respect)

- **Proxy:** `proxy(stream_2d_uint8, n_features=None) -> float in [0,1]`. Deterministic.
  Higher = more coherent structure. `stream_2d` is `(T, n_features)` binary. The ablation
  operator handles per-feature `rho` by calling the proxy on column-replaced streams; the
  proxy itself only returns a scalar.
- **Ablation:** `ablation(stream, proxy, n_features=None, *, rng=None, center=True) -> dict`
  with keys `rho` (dict feature->value, cohort-mean-centered when `center=True`),
  `c_ablated`, `centered` (and `clusters` for A3). LOO/Shapley/CorrCluster all share this.
- **Induction:** `induce_weights_multi(stream, n_features=None, *, proxy=None, ablation=None,
  rng=None, beta=4.0) -> {rho, w, c_ablated, centered}` with `w(j) = sigmoid(beta*rho(j))`.

### 3.4 Proxy family identities (each a structurally distinct lens; this distinctness is the point)

| K | Module | Family | Key mechanism |
|---|--------|--------|---------------|
| form B multi | `predictive_logloss_multi` | predictive log-loss, no penalty | joint conditioning on previous full feature vector, Laplace-smoothed |
| K1 multi | `compression_delta_multi` | universal compression | zstd level 3 on 2-byte-per-step encoding (10 active + 6 padding bits); `C = 1 - len(compressed)/len(uncompressed)` |
| K2 | `ngram_mdl` | explicit MDL with model penalty | per-feature factorized bigram, 2-part MDL (Rissanen `0.5*num_params*log2(T)`), `num_params = 2*n_features` |
| K3 | `neural_prequential` | neural online cross-entropy, no penalty | single-layer GRU (hidden=64), per-feature sigmoid heads, strict online prequential SGD (lr=0.01), `NEURAL_SEED=7`, torch CPU-deterministic |
| K4 | `mdl_hmm` | latent-variable model + MDL cardinality selection | factorized-Bernoulli HMM, Baum-Welch EM, MDL search over `H in {1,2,3,4}`, `num_params(H)=H(H-1)+H*n+(H-1)`, `HMM_SEED=0` |
| K5 | `lempel_parsing` | non-coding pattern counting | bit-level LZ76 phrase parse (numba Kaspar-Schuster) on the unpacked K1 byte stream; no entropy coder |

K4 is the only proxy with a latent variable AND an explicit complexity penalty. K3/K4 share
K2's per-feature factorization, so K-vs-K2 comparisons isolate the model-class difference.
K1 and K5 share the same underlying bits (K1 compresses bytes via zstd; K5 parses bits via
LZ76) so their difference traces to the parsing/coding boundary, not representation drift.

### 3.5 Ablation operators

| A | Module | Mechanism |
|---|--------|-----------|
| A1 | `loo_multi` | leave-one-out: replace one feature column with Bernoulli(0.5); `rho = C_full - C_ablated`, centered. |
| A2 | `shapley_multi` | Shapley value over `k=64` sampled coalitions; replace-with-uniform from kept set; cohort-mean centered. EXPENSIVE. |
| A3 | `correlation_cluster` | Pearson signed-correlation clustering (threshold `DEFAULT_CORRELATION_THRESHOLD = 0.15`), connected components, ablate cluster-wise. Multi-feature-native (no 1-D analog). |

### 3.6 Coders -- `cit/coders/selective.py` (v0.6.1, built)

The selective compression coder (the corrected `H(Z)` theorem; Section 7.3). `selective_encode` /
`selective_decode` (a bit-exact 32-bit Witten-Neal-Cleary arithmetic coder on the merged source) +
a zstd variant + `merged_source_entropy`. It replaces the paper's weighted-typical-set coder, which
was found UNSOUND for non-constant w (Thm 5.1; Section 7.3).

### 3.7 Tests and gating

Fifteen test files. Total **390 tests: 272 fast + 100 slow + 18 very_slow (1 xfail = Seam 1).**

| File | Covers |
|------|--------|
| `test_shannon_recovery.py` | the boundary-condition spine (H_w/I_w collapse to Shannon at w=1); `SEED=42`. |
| `test_induction_pipeline.py` | v0.2 single-symbol induction; `STREAM_SEED=42`, `ABLATION_SEED=123`. |
| `test_cross_proxy_validation.py` | v0.3 cross-proxy (form B vs K1) at the 1-D level (threshold 0.7). |
| `test_cross_ablation_validation.py` | v0.4 cross-ablation (A1 vs A2) sign agreement + Spearman >= 0.7. |
| `test_multi_feature_substrate.py` | the v0.5 program: substrate, all 6 proxies x 3 ablations, the 15-pair cross-proxy matrix, the noise-only falsifiability (`TestNoiseOnlyFalsifiability`), Seam 1 xfail, A3 cluster recovery (observational). |
| `test_capacity.py` | v0.6.0: boundary spine (BSC/Z recover Shannon capacity), the CORRECTED Binary Coherence Channel fixture, P2, determinism, analytic-gradient FD-check. |
| `test_selective_coder.py` | v0.6.1: arithmetic round-trip bit-exactness, lossless-on-S_delta, achievability `<= H(Z)+eps`, boundary collapse, H_w-as-measure. |
| `test_selective_compression_empirics.py` | v0.6.2: win-margin `Delta_frac >= 0.20` on iid/Gilbert-Elliott/TCUN; boundary `Delta = 0`. |
| `test_metacoherence_d1.py` | v0.7.0: D1 substrate structure (seed-stable invariants -- max-share<0.40, distractor flatness marginal-relative, class separation, B/D bands, bit-exact per seed). |
| `test_categorical_proxies.py` | v0.7.0: categorical marginal-relative K1-K5 (feature-major encoder, time-shuffle surrogate baseline, determinism). |
| `test_categorical_ablations.py` | v0.7.0: categorical A1/A2/A3 (uniform-over-alphabet replacement). |
| `test_metacoherence_r2.py` | v0.7.0: R2 + cross-tab machinery (spearman incl. zero-variance NaN; `recovered_properties`; `partition_diagnostic` +0.43 bound). |
| `test_crossing_proxies.py` | v0.7.0 decoupling control: K3b/K2b byte-stream crossings -- shared-with-K1 representation, marginal-relative, recover A/D on D1 (6 fast + 1 slow). |
| `test_decoupling_control.py` | v0.7.0 decoupling control: the metric -- twin-excluded `crossing_delta`, 18/20 x two-band assignment, the TOTAL nine-cell concordance, end-to-end pipeline (20 fast + 1 slow). |
| `test_r1_persistence.py` | v0.7.1 R1 (Section 8.5): bit-exact sibling generator, RNG-preserving perturbation, the validation gate (distractors ~0, f0/A above them), documented-null f2/f5, determinism, Cohen's d helper (11 fast). |

**Gating** (`pyproject.toml addopts = -m 'not slow and not very_slow'`):
- **fast** (default `pytest`, ~70s): everything cheap (form B / K1 / K2 proxies and their A1/A3/A2, the boundary spine, the noise-falsifiability tests, the v0.7 categorical D1 / R2 / decoupling-metric tests).
- **slow** (`-m slow`): LOO + CorrCluster for K3/K4/K5 (structured AND noise), proxy invariants, the A2 cheap-proxy noise sample, plus the v0.7 slow tests (the K3b crossing-recovery on D1; the decoupling-control end-to-end pipeline at small T). CI workflow `slow.yml` runs on every push, `timeout-minutes: 60`.
- **very_slow** (`-m very_slow`, workflow_dispatch only): Shapley (A2) for K3/K4/K5. K4 Shapley ~2.1h (under 6h hosted ceiling); K5 ~135 min; K3 ~4.3h (local-gated, exceeds hosted ceiling). Hosted `very_slow.yml` runs `-k "not K3"` (K4+K5 families), `timeout-minutes: 350`.

(Note: the `markers` docstrings in `pyproject.toml` still say "K_5 LZ76" only -- a stale
comment predating K3/K4 and the noise tests. Harmless; not corrected as of this writing.)

### 3.8 v0.7 metacoherence + decoupling control (`cit/metacoherence.py`, `cit/proxies/crossing.py`)

**R2 / cross-tab machinery.** `compute_cell(proxy, ablation, seed, T)` runs one D1 grid cell end-to-end
(generate -> categorical proxy -> categorical ablation -> induced w); `compute_grid` fans the 5x3 grid;
`cross_philosophy_r2` is the median Spearman over cell pairs; `recovered_properties` / `build_cross_tab`
give the per-property recovery cross-tab; `partition_diagnostic` is the read-only +0.43 shared-top-k
bound (a Spearman below the floor PROVES the two top-k partitions differ). `spearman` is implemented
locally (no scipy), returning NaN on zero rank-variance (the honest treatment of null cells).

**Decoupling-control metric (the twin-excluded nine-cell concordance).** Pure functions over induced-w
vectors. Two co-primary crossings live in `cit/proxies/crossing.py`: K3b = the K3 neural-prequential
functional, K2b = the K2 bigram-MDL functional, each applied to the IDENTICAL feature-major byte-stream
encoding + time-shuffle surrogate baseline (`SHUFFLE_SEED=0`) that K1/K5 use -- so {K1, K5, K3b, K2b}
share representation and differ ONLY in the complexity functional. The decision Delta is TWIN-EXCLUDED
and cross-functional: `CROSSING_REFS = {K3b: twin K3, M=(K2,K4), B=(K1,K5); K2b: twin K2, M=(K3,K4),
B=(K1,K5)}`, and `crossing_delta = mean Spearman(w_crossing, w_{M\\twin}) - mean Spearman(w_crossing,
w_{K1,K5})` (the crossing's OWN twin is removed from M, so a same-functional / different-serialization
twin correlation cannot inflate the modeling side). `crossing_assignment` maps the per-seed Delta list
to {MODELING, BYTE, UNSTABLE} via `DECOUPLE_STABILITY_N = 18`/20 sign-count x a two-band magnitude
(`DECOUPLE_CONFIDENT = 0.40`, `DECOUPLE_WEAK = 0.10`). `concordance_verdict` is TOTAL over all nine
(K3b x K2b) cells (both-MODELING = PHILOSOPHY, both-BYTE = REPRESENTATION-ARTIFACT, opposite-decisive =
PROXY-SPECIFIC-SPLIT, any-UNSTABLE = INCONCLUSIVE with a recorded single-crossing lean). `twin_spearman`
is a REPORTED representation-invariance sanity check, NEVER a decision input. `decoupling_control_verdict`
/ `compute_decoupling_run` tie it together over the 20-seed ensemble; `scripts/run_decoupling_control.py`
is the run driver; `results/decoupling_control/verdict.json` + 20 `seed_*.json` are the committed artifact.

---

## 4. The v0.5 robustness program (COMPLETE) -- results and invariants

v0.5.0 substrate -> v0.5.1 K2 -> v0.5.2 K5 (Seam 1 surfaced) -> v0.5.3 K3 -> v0.5.4 K4
(Seam 1 specificity evidence) -> v0.5.5 capstone (noise-only falsifiability + Seam 1 resolved).

### 4.1 Cross-proxy convergence matrix (structured substrate)
All 15 off-diagonal pairs of {form B, K1, K2, K3, K4, K5} under each of A1, A2, A3 (45 cells)
clear **Spearman rho >= 0.5** (the multi-feature threshold, calibrated 2026-05-26). Built
incrementally; consolidated at the capstone.

### 4.2 Cross-ablation convergence
A1 vs A2 per-symbol sign agreement (strict) + Spearman rho >= 0.7 (the 1-D / ablation-axis threshold).

### 4.3 Noise-only counterfactual (the falsifiability spine, v0.5.5)
For each off-diagonal pair: structured Spearman `>= 0.5` AND noise-only Spearman `< 0.3`
(`T_NOISE = 0.3`, locked). Asserted on A1 + A3 for all 15 pairs; A2 (Shapley) sampled on the
3 cheap-proxy pairs (full A2-on-noise would be a second ~8h very_slow tier for marginal value).
Calibration (locked seeds), structured vs noise-only cross-proxy Spearman:

| Ablation | structured (min/mean/max) | noise-only (min/mean/max) |
|----------|---------------------------|---------------------------|
| A1 (LOO) | 0.571 / 0.753 / 0.948 | -0.390 / -0.049 / 0.000 |
| A3 (CorrCluster) | 0.583 / 0.754 / 0.985 | -0.390 / -0.049 / 0.000 |
| A2 (Shapley, cheap) | 0.733 / 0.794 / 0.855 | -0.297 / -0.099 / 0.000 |

No pair has positive convergence on noise under any ablation. (Many noise pairs are exactly
0.000 because proxies that clip C to a constant on noise yield tied rho vectors -> Spearman 0.)

### 4.4 Seam 1 (RESOLVED at v0.5.5; stays xfail)
`(K5, K2)` under A2 Shapley = **0.491**, just under 0.5. Surfaced v0.5.2. Resolved
`(K5, K2)`-SPECIFIC: of all `(X, K2)` pairs under A2, only K5 misses; K3, K4 (0.830),
form B, K1 all clear. So the divergence is particular to K5's LZ76 phrase dictionary vs K2's
factorization under random-coalition ablation, and does NOT generalize -> the framework's
operating envelope is NOT restricted. Mechanically `@pytest.mark.xfail(strict=True)` in
`test_multi_feature_substrate.py::TestCrossProxyConvergenceMulti::test_K5_vs_K2_under_A2`.
A strict XPASS forces re-evaluation. **Do not "fix" silently.**

---

## 5. Locked constants, conventions, environment

### 5.1 Locked constants (pre-registered; change only with a version bump + pre-reg amendment)
| Constant | Value | Where | Role |
|----------|-------|-------|------|
| `beta` | 4.0 | `cit/induce.py`, `cit/induce_multi.py:BETA` | weight-map sensitivity `w=sigma(beta*rho)` |
| `SEED` | 42 | `tests/test_shannon_recovery.py` | Shannon-recovery stochastic tests |
| `STREAM_SEED` | 42 | `test_induction_pipeline.py`, `test_cross_proxy_validation.py`, `test_cross_ablation_validation.py`, `test_multi_feature_substrate.py` | synthetic-stream generation |
| `ABLATION_SEED` | 123 | same four test files | ablation RNG (LOO/Shapley/CorrCluster) |
| `NEURAL_SEED` | 7 | `cit/proxies/neural_prequential.py` | K3 GRU init/SGD |
| `HMM_SEED` | 0 | `cit/proxies/mdl_hmm.py` | K4 Baum-Welch EM init |
| `DEFAULT_CORRELATION_THRESHOLD` | 0.15 | `cit/ablations/correlation_cluster.py` | A3 clustering edge threshold |
| cross-proxy R2 (multi) | Spearman >= 0.5 | `test_multi_feature_substrate.py:R2_THRESHOLD` | convergence floor |
| cross-proxy R2 (1-D) | Spearman >= 0.7 | v0.3/v0.4 tests | 1-D convergence floor |
| cross-ablation | Spearman >= 0.7 + sign agreement | v0.4 | A1 vs A2 |
| `T_NOISE` | 0.3 | `test_multi_feature_substrate.py` | noise-only falsifiability ceiling |
| collapse tol | 1e-12 (algebraic); empirical atol in pre-reg | tests | boundary-condition precision |

### 5.2 Working conventions
- **One sub-step per "proceed."** Hand steering back; no unsupervised bulk output.
- **Pre-register before implementation.** If structural findings emerge, pre-register
  honestly rather than silently adjusting thresholds. The amendment pattern: bump version,
  add a dated entry to `pre_registration.md`'s history (most recent last), update the design
  memo in the same commit, never silently edit a lock.
- **Surgical Python edits** via `python << 'PYEOF'` with BOTH guards:
  `assert src.count(old) == 1` (anchor) AND `assert <new-token> not in src` (idempotency).
  Heredocs use `MULTIEOF`, not `EOF`. (Markdown/config: direct edits are fine.)
- **ASCII-only in code payloads.** Unicode allowed in README.md / pre_registration.md prose
  (and this design doc keeps ASCII for consistency with `design/`).
- **Parse at the bit level**, not byte level, where byte-level clips a metric to zero
  (the K2 joint-bigram and K5 byte-level amendments both stemmed from clip-to-zero).
- **Commits:** two `-m` flags, dense paragraph body; version strings `"vX.Y.Z: subject"`.
  No `Co-Authored-By` trailer. Commit/push only when asked.
- **Per-version release checklist** (do not miss any): bump `pyproject.toml` AND
  `CITATION.cff` (version + `date-released`); update README status row + counts; refresh
  CLAUDE.md; pre-reg amendment (if behavior); then commit + annotated tag `vX.Y.Z` +
  `gh release create` (which mints the Zenodo version DOI). The README DOI badge is the
  concept DOI (auto-resolves to latest) and must not be edited per the 2026-05-26 convention.

### 5.3 Environment & determinism
- Python 3.11/3.12. `python3.12 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`.
- Deps: `numpy<2`, `zstandard`, `numba>=0.60`, `torch>=2.0,<2.3`. (No scipy: Spearman is
  hand-implemented with midrank ties in the test file.)
- Bit-exact determinism is load-bearing for the convergence claims. x86<->arm64 migration
  breaks bit-exact CI parity (multi-day measurement-and-amendment lift, not a quick port).
- **Operational gotcha:** heavy numba/pytest background runs, when killed, can leave orphaned
  child processes that consume CPU and starve later runs (caused a ~12h false "hang" once).
  Launch long jobs as plain `python/pytest` under the harness background (no `nohup`/`&`);
  do not overlap heavy runs; verify with `pgrep -fl python` and `pkill -9 -f <script>` after killing.

---

## 6. Pre-registration discipline (the method, proven over v0.5)

The pattern that worked for K3, K4, and the v0.5.5 capstone, and that v0.6 should follow:

1. **Gather state** (boot: README, pre-reg, git, fast suite).
2. **Due-diligence BEFORE locking.** Run an empirical pre-check (often two independent
   throwaway implementations that must agree) to settle the one decisive risk -- e.g. "does
   the metric clip to zero on this substrate?" (K2/K5) or "what is the noise baseline?"
   (v0.5.5 threshold). Cite the measured numbers in the amendment.
3. **Surface the genuine design choices** to Benjamin (narrow vs rich, threshold value,
   compute scope) and get sign-off.
4. **Write the pre-reg amendment** (definition, locked constants, rationale, expected
   values, gating, the honest gaps). Update the design memo in the same commit.
5. **Implement** to match the lock; verify it reproduces the pre-registered expectation.
6. **Wire tests**, assign markers, run fast+slow green; expensive tiers separately.
7. **Ship** (the release checklist).

If a measured result contradicts the lock (e.g. a pair lands < threshold), record it
honestly as a seam (`xfail(strict=True)`) with a resolution version -- do not tune to pass.

---

## 7. v0.6 -- Capacity, Coder, Selective Compression (SHIPPED -- program complete)

**Decided (2026-06-23):** sequence is **capacity estimator first (v0.6.0)**, then coder
(v0.6.1), then Selective Compression empirics (v0.6.2). Source specs come from the papers
(Benjamin supplied them; see Section 10). The capacity estimator is the most self-contained,
low-risk deliverable; the coder and the soundness gap are where the real authoring burden is.

### 7.1 The theorems (verbatim from `cit formal.docx` = JAMFFO-2, "Capacity and Compression Theorems")

**Coherence Capacity Theorem (Thm 4.1).** For a DMC `p(y|x)` and weight `w: X -> [0,1]`,
a rate R (bits/use) is achievable for coherence-relevant transmission iff
`R < C_C = max_{p(x)} I_w(X;Y)`. Reliability = block error `Pe(n) -> 0` AND the decoder
recovers every symbol whose weight exceeds any fixed `delta > 0`. Achievability: random
coding + coherence-joint-typicality decoding. Converse: weighted Fano +
single-letterization `I_w(X^n;Y^n) = sum_i I_w(X_i;Y_i) <= n*C_C`. **Cor 4.4:** `w=1 => C_C = C`
(Shannon channel capacity recovered) -- the boundary condition.

**Selective Compression Theorem (Thm 5.1).** For an i.i.d. source `p(x)` with weights
`w(x) in [0,1]`, any uniquely-decodable lossless code whose decoder must reproduce every
symbol with `w(x) > delta` has expected per-symbol length `L >= H_w(X)`, and for every
`eps>0` there is a block-length and coding scheme achieving `L <= H_w(X) + eps`. Converse:
Kraft-McMillan with weighted typical-set counting. `w=1 => L >= H(X)` (Shannon).

**Weighted AEP.** `-(1/n) sum_i w(x_i) log p(x_i) -> H_w(X)` in probability; equivalently
`Pr{X^n in T_w,eps^n} -> 1`. Coherence-typical set
`T_w,eps^n(X) = { x^n : | -(1/n) sum_i w(x_i) log p(x_i) - H_w(X) | < eps }`.
Proofs: weighted WLLN (Lemma A.1) + Chebyshev/Chernoff (A.2); cardinality (A.3)
`(1-d) 2^{n(H_w-eps)} <= |T| <= 2^{n(H_w+eps)}`.

### 7.2 v0.6.0 -- Coherence capacity estimator (LOCKED 2026-06-23)

Pre-registered in `pre_registration.md` (the `## v0.6` section + the 2026-06-23 amendment entry).
Due-diligence settled the decisive risk (does a numpy simplex maximizer reproduce the fixture and
the boundary) before locking. What is locked:

- **Definition:** `C_C = max_{p(x)} I_w(X;Y)` for fixed DMC `p(y|x)` and fixed `w(x)`,
  over the input simplex. Reuse `cit/information.py:I_w`.
- **Boundary unit test (the spine):** `C_C(w=1) == Shannon channel capacity` to tolerance,
  mirroring `test_shannon_recovery`. Use a channel with closed-form Shannon capacity (BSC, Z-channel).
- **Binary Coherence Channel fixture -- CORRECTED (Sec 6 erratum).** The paper's Sec 6
  `C_C(eps)=0.5(1+eps)` (identity channel, `w=(1,eps)`, uniform input) is `I_w` at UNIFORM input,
  NOT the capacity: `I_w = H_w = -q log2 q - eps(1-q) log2(1-q)` is maximized at `q* < 0.5` for
  eps<1, so `0.5(1+eps)` is only a lower bound (equal at eps=1). Locked TRUE capacity: eps=0 ->
  0.530738 (=`1/(e*ln2)`, `q*=1/e`); 0.25 -> 0.639687; 0.5 -> 0.755588; 0.75 -> 0.876210; 1.0 ->
  1.0. No closed form for general eps; only the endpoints are exact. Erratum affects ONLY the Sec 6
  example, NOT Capacity Theorem 4.1 (`C_C = max_p I_w`, correct). Flagged for author erratum.
- **CHOICES LOCKED at pre-reg (the papers leave these to us; now settled):**
  - *Solver.* Projected-gradient ascent on the simplex with a DETERMINISTIC multi-start set
    (centroid + n vertices + resolution-m=20 lattice), best local optimum; analytic gradient
    FD-checked; `tol=1e-10`, `max_iter=2000`; no RNG (bit-exact, no new seed). Small-alphabet
    fixtures only; larger alphabets need a seeded-sampling amendment. Blahut-Arimoto NOT used.
  - *Concavity: OPEN.* Not proven (the `w(x)` factor breaks the standard argument). Multi-start
    agreement is the empirical uniqueness stand-in, asserted on the fixtures. No guarantee claimed.
  - *Tolerance / iteration cap:* `tol=1e-10`, `max_iter=2000`; test atols 1e-6 (boundary), 1e-8
    (closed-form anchors; corrected from 1e-9 post-implementation -- the locked tol floors at
    ~1e-9 value accuracy on the flat eps=0 max), 1e-5 (grid-verified eps).
  - *delta (must-preserve threshold):* the capacity value is delta-independent; deferred to v0.6.1.
  - *Test channels:* BSC(p in {0.1,0.25}) + Z-channel(f=0.5) for the boundary; the corrected
    Binary Coherence Channel for the fixture.
- **Asserted invariants (locked):** boundary collapse (BSC + Z, atol 1e-6); the corrected fixture
  (closed-form anchors atol 1e-8, grid-verified eps atol 1e-5, `q*<0.5` strict); `C_C(eps) >=
  0.5(1+eps)`; `0 <= C_C <= C_Shannon` (P2); determinism (bit-identical); monotonicity of `C_C` in
  a uniform weight scale. Tests FAST in `tests/test_capacity.py`.

### 7.3 v0.6.1 -- Selective compression coder (LOCKED 2026-06-23; Thm 5.1 repaired)

Pre-registered in `pre_registration.md` (the v0.6 "Selective compression coder" subsection + the
2026-06-23 v0.6.1 amendment). A 4-agent adversarial analysis (confirmed against the paper text)
found the paper's Thm 5.1 UNSOUND for non-constant w -- RESOLVED-NEGATIVE -- so the repo builds the
corrected theorem instead.

- **Thm 5.1 is unsound for w != 1 (resolved-negative).** Achievability `L <= H_w + eps` and the
  App A.2 cardinality bound `|T| <= 2^{n(H_w+eps)}` both fail: w-typicality constrains the WEIGHTED
  log-prob `~ H_w`, but the typical set's SIZE is governed by the RAW `-log p(x^n)` (enumerated:
  `|T|=6 > 5.28`; `|T|=15 >> 5.43`). Under the threshold criterion only `S_delta={x:w(x)>delta}` must
  be reproduced, so the true floor is the merged-source entropy `H(Z)`, which can exceed `H_w`. The
  paper's own Sec 5.4 binary example is the counterexample. Holds only at `w=1` (Shannon).
- **H_w recast (kept):** `H_w = E_p[w(X)(-log p(X))]` stays as the "bits that matter" MEASURE, not a
  compression rate. `cit/information.py:H_w` unchanged.
- **Corrected theorem (Option A, built):** compress to `H(Z)`, `Z=(S_delta union {*})` -- reproduce
  `S_delta` exactly, collapse all don't-cares to one token. Converse `L >= H(Z)`; achievability
  `L <= H(Z)+eps` (entropy coding of Z); boundary `S_delta=X => H(Z)=H(X)` (Shannon spine);
  `H(Z) <= H(X)` always. H(Z) is partition-driven (the threshold, not the graded weights, sets it;
  the graded weights live in the H_w measure).
- **Coder (`cit/coders/selective.py`):** "merge -> entropy-code." Primary = static arithmetic/range
  coder on Z (rate `-> H(Z)+eps`, bit-exact); practical variant = zstd on the merged byte stream
  (reuses K1). `delta` explicit; decoder reproduces `S_delta` exactly + a fixed placeholder for `*`.
- **Invariants:** lossless on `S_delta`; arithmetic rate `<= H(Z)+0.02` at `N=200k`; `H(Z) <= H(X)`;
  coherence saving vs weight-blind when `>= 2` don't-cares; boundary collapse; determinism. Fast tier.

### 7.4 v0.6.2 -- Selective Compression empirics (LOCKED 2026-06-23)

Pre-registered in `pre_registration.md` (the v0.6 "Selective Compression empirics" subsection + the
2026-06-23 v0.6.2 amendment). The win-margin demonstration of the corrected coder (Section 7.3), on
the SOUND `H(Z)` footing (the floor is `H(Z)`, NOT `H_w`).

- **Win metric:** fractional saving `Delta_frac = (rate_blind - rate_selective)/rate_blind`
  (arithmetic coder), where weight-blind = `delta` below all weights (no merge, full lossless). Both
  coders are lossless on `S_delta`, so the win is at ZERO coherence-retention cost (equal-retention,
  lower-rate -- cleaner than the paper's equal-rate/higher-retention asymmetry).
- **Falsifiable claim (two-sided):** per structured substrate `Delta_frac >= WIN_MARGIN = 0.20` AND
  lossless on `S_delta`; at the boundary (`S_delta = X`) `Delta = 0` exactly. Falsified if the saving
  falls below 0.20 on structure, is non-zero at the boundary, or any `S_delta` symbol is corrupted.
- **Substrates (locked seeds, N=100k):** iid (`rng(42)`), Gilbert-Elliott memory (`rng(1)`), TCUN
  toggle+noise (`rng(2)`). Calibration (arith `Delta_frac`): iid 0.492, G-E 0.411, TCUN 0.307;
  boundary 0.000. Margin 0.20 sits below the 0.307 floor with headroom. The v0.5 multi-feature
  substrate is per-feature-binary, not a symbol stream -- deliberately excluded.
- **Gating:** fast. `tests/test_selective_compression_empirics.py`. Completes the v0.6 program.

### 7.5 KNOWN GAPS AND RISKS (carry these into the v0.6 pre-reg, honestly)

1. **No capacity solver / no concavity result IN THE PAPERS.** Authored repo-side: solver LOCKED
   v0.6.0 (deterministic projected-gradient multi-start); concavity remains OPEN (multi-start
   agreement is the empirical stand-in). See Section 7.2.
2. **The practical weighted coder is constructed nowhere** -- RESOLVED at v0.6.1: the weighted
   typical-set coder is unsound (Section 7.3); the corrected `merge -> entropy-code` selective coder
   (`cit/coders/selective.py`) is built against `H(Z)` and demonstrated in v0.6.2.
3. **App A.2 soundness flag -- RESOLVED-NEGATIVE at v0.6.1 (2026-06-23).** The typical-set
   cardinality bound `|T| <= 2^{n(H_w+eps)}` is false for `w != 1`: w-typicality controls the
   WEIGHTED log-prob `sum_i w(x_i)(-log p(x_i)) ~ H_w`, which does NOT bound the RAW
   `-log p(x^n)`, so the bound and the `H_w` achievability rate fail (enumerated counterexamples).
   Adversarially verified (4-agent) and confirmed against the paper text; Thm 5.1 holds only at
   `w=1`. Both the converse and achievability to `H_w` are unsound; the capacity theorem (Sec 4) is
   UNAFFECTED. Repaired in v0.6.1: `H_w` demoted to a measure, operational floor replaced by the
   merged-source entropy `H(Z)` (Section 7.3 + the 2026-06-23 v0.6.1 amendment in `pre_registration.md`).
4. **No finite-blocklength theory** (paper Sec 9 defers to Polyanskiy-Poor-Verdu). Any finite-n
   empirical correction needs its own pre-registration.
5. **No numeric reproducibility constants** in any document (no seeds/tolerances/alphabet sizes
   for the estimator/coder; the paper's LM simulation reports numbers with no seed/code).
   All repo-side; set them at pre-reg.
6. **Robustness-bar mismatch across docs** (engineering wants median Spearman > 0.8;
   Metacoherence R2 >= 0.7; repo cross-proxy 0.5). Reconcile in v0.6.2: those higher bars are
   validation-program bars, not capacity/coder bars.

---

## 8. v0.7 -- Cross-domain validation (Metacoherence)

> **STATUS (HEAD `df025a3`).** D1 is BUILT; the decoupling control is BUILT + RUN (verdict INCONCLUSIVE
> -- Section 8.3); the v0.7 PROGRAM is REFRAMED (Section 8.4): D1's role is ESTIMATOR COVERAGE-CALIBRATION
> (not R2 pass/fail), R2 is a non-falsifying DIAGNOSTIC, and R1 + the v0.6.2 functional win are PRIMARY.
> **v0.7.1 R1 (persistence) is BUILT + RUN + CLOSED as CALIBRATION** (Section 8.5: necessary-not-sufficient
> AND mechanism-confounded; D-led; partial d-matrix K1 FAILS / K2 PASSES). **D2 (Pfam) R1 is PRE-REGISTERED**
> (Section 8.6). The architecture below (M5, the eight-cell matrix, the locked statistical thresholds) stands
> as the PLAN; read the R2-as-gate language in 8.1-8.2 as SUPERSEDED by 8.4 (R2 is now a convergence flag, not
> a falsification gate) and the eight-cell matrix as pending re-derivation.

The cross-domain architecture from Metacoherence. Tests that the SAME `rho` signal recovers across
distinct domain substrates `D1, D2, D3`. **v0.7.0 LOCKED 2026-06-23** (pre_registration.md: the
`## v0.7` section + the 2026-06-23 v0.7.0 amendment): D1 = a 3-state hidden semi-Markov substrate
(8 alphabet-8 features encoding 4 properties A/B/C/D + 3 distractors; params MI-balanced so no
property exceeds 40% of recoverable info), its exact-by-construction M5 partition ({f0..f4} vs
{f5..f7}), and R2 (cross-philosophy median Spearman `> 0.6`, CI `> 0.4`) via the categorical 5x3
grid with the LOAD-BEARING marginal-relative coherence requirement (else skewed-marginal distractors
read as coherent). Sequenced: v0.7.0 D1+M5-partition+R2; v0.7.1 R1 (persistence); v0.7.2 R3
(interventions); then D2 (Pfam, CC0), D3 (FOMC), and the M5 + eight-cell capstone. Four conditions:
R1 (persistence prediction), R2 (cross-philosophy convergence), R3 (intervention asymmetry), and:

- **M5 cross-domain admissibility gate** (operationalized in Metacoherence): mean-w over
  coherence-bearing vs noise features, rank-normalized, within a factor-of-2 across all domain
  pairs for at least 3 of 5 estimator classes.
- **The eight-cell outcome interpretation matrix** (Metacoherence Sec 8.3-8.4) to be reproduced
  verbatim and bound to outcomes in advance.
- **M-conditions** (the weight admissibility axioms; the principled-quantity layer): see Section 9.

v0.7 has empirical content only because v0.3-v0.6 anchored operator-invariance and the
operational theorems on a single substrate first.

Locked statistical thresholds (Metacoherence Sec 8.7): R2 median Spearman > 0.6 (CI > 0.4);
R1 Cohen's d > 0.5 (CI > 0.3, p < 0.01); R3 structural/interpretive ratio > 3.0 (CI > 2.0); M5
factor-of-2 rank-normalized, 3-of-5 estimators; Bonferroni across 51 cells; bootstrap B = 1000.
Data sources for the real domains are FREE/public (confirmed 2026-06-23): D2 Pfam = CC0 via
EBI/InterPro (+ HF/Kaggle scrapes); D3 FOMC = U.S. public domain (Fed, HF `vtasca/fomc-statements`).

### 8.1 v0.7.0 build plan (D1 + M5 partition + R2) -- COMPLETE (built `d9eb3b5` + `823928a`; retained for reference)

Sliced for reviewability (pre-reg: 2026-06-23 v0.7.0 amendment + the `## v0.7` section). All three slices are BUILT + committed:
- **Slice 1 -- `cit/data/hsmm_d1.py` (the generator).** Locked construction: 3-state HSMM, negbinom
  sojourns (mean 200, dispersion r=6), T=50k, N_REPLICATES=20; 8 features x alphabet 8: f0
  regime-conditional (Property A, F0_scale=1.7); f1 = g(f0,f2,f4 @ t-12) w.p. 0.35 else uniform
  (Property B, lag L=12); f2 ~ uniform, f3 = (f2 + C_VAL[state,bucket]) % 8 (Property C ADDITIVE
  MASK -- individually uniform, jointly recover regime); f4 drift-mode emission (Property D,
  std=0.10, peak=1.0); f5/f6/f7 uniform/Zipf/low-freq distractors. Structure test: MI diagnostics
  reproduce the calibration (I_A=0.76, I_B=0.46, I_C=0.34, I_D=0.58), distractors structurally flat,
  bit-exact per seed. The LOCKED construction already encodes the two bug-fixes found in
  due-diligence (C MUST be additive-masked or it leaks regime info into each feature singly; D's
  drift must be strong enough to clear the noise floor but not dominate).
- **Slice 2 -- categorical proxy generalization.** K1/K5 are alphabet-agnostic (byte/bit). K2
  (per-feature categorical n-gram MDL), K3 (GRU softmax heads), K4 (categorical-emission HMM) are
  generalized from binary. ALL must measure coherence MARGINAL-RELATIVE (predictive: H_marginal -
  H_pred; compression: structural vs marginal-only baseline) -- the load-bearing lock (8.2).
- **Slice 3 -- the 5x3 grid + R2 + cross-tab.** Run all 15 cells on D1; induced w over 8 features;
  cross-philosophy median Spearman > 0.6 (CI > 0.4, bootstrap B=1000, block=200); the 15x4
  property-recovery cross-tab (D1 is CHARACTERIZED, not pass/failed -- expected pattern: K1xA1
  recovers A only; K3xA2 recovers A,B,C,D; A1 misses C; short-context estimators miss B).

### 8.2 D1 lessons + empirical risks (carry into the build)

- **Marginal-relative coherence is LOAD-BEARING.** D1's distractors (Zipf, low-freq) have skewed
  marginals BY DESIGN. A uniform-baseline coherence measure mistakes that skew for structure -- a
  naive GRU did exactly this in due-diligence (the low-freq distractor scored HIGHEST rho). Every
  estimator's coherence on D1 (and any non-marginal-matched substrate) must factor out the marginal.
  The v0.5 substrate was marginal-matched (p=0.5) so this never arose; D1 is the first substrate
  where it bites. This is the single most important implementation constraint for Slice 2.
- **Property B recovery is uncertain.** Whether the real categorical K3 (GRU, online SGD) actually
  learns the 12-step lag coupling is open; if not, B is recovered only by K4 (or not at all) -- a
  cross-tab finding, recorded not tuned. (Lag was reduced 150 -> 12 in calibration precisely to make
  it GRU-learnable; a 3-state HMM cannot buffer 150 steps either, and a fully-deterministic coupling
  saturated whatever caught it -- hence B_keep=0.35 partial determinism.)
- **R2 is a DIAGNOSTIC, not a pass/fail gate (post-reframe, Section 8.4).** The cross-tab EXPECTS
  estimators to diverge on which properties they recover; on D1's A1 column the median fell FAR below 0.6
  (`~ -0.08` at the preview), and the reframe established that this divergence is a COVERAGE CEILING
  (cross-extractor w-agreement certifies only shared-coverage structure), NOT a falsification. The
  0.6/0.4 numbers are KEPT as a convergence flag; a sub-0.6 median is recorded as a coverage annotation,
  NOT a seam. Falsifiability is relocated to R1/R3. The earlier "record as a seam, do not adjust"
  instruction is SUPERSEDED -- divergence here is non-falsifying, not a seam.
- **The exact Sec 5.4 ceiling** (40% of w-variance under K3xA1) is verified in-build with the real
  marginal-relative K3; the MI-balanced generator params stand unless that verification forces a
  recorded amendment (the K4 / v0.6.0 post-impl-correction discipline).

### 8.3 Decoupling control -- RESULT (INCONCLUSIVE, necessary-not-sufficient)

The instrument-validity reading (D1's `{K1,K5}|{K2,K3,K4}` split is collinear with the byte-stream vs
categorical-native encoder boundary, so philosophy and representation are CONFOUNDED) was probed by a
pre-registered DECOUPLING CONTROL (pre-reg 2026-06-23; result 2026-06-24; commits `7cca0c5` -> `d840553`).
The control crosses two MODELING functionals onto the byte stream -- K3b (lowest-distortion) and K2b
(mechanistically targeted at the factorized C-blindness) -- holding representation constant while
philosophy varies, and asks which block each crossing joins (the twin-excluded nine-cell metric, Section
3.8). Run at full-T=50000 over the 20-seed ensemble (A1-only, 20/20 seeds, 0 fail):

- **Verdict: INCONCLUSIVE**, cell (K3b = MODELING, K2b = UNSTABLE). K3b MODELING-CONFIDENT (n_M 20/20,
  median Delta +0.506, 90% CI [+0.14, +0.96] excludes 0); K2b UNSTABLE (n_M 17/20 -- misses the locked
  18/20 by ONE seed; median +0.363, CI [-0.12, +0.64] straddles 0). Twins K3b-K3 0.88, K2b-K2 0.80
  (faithful crossings, so the borderline is genuine, not a broken instrument).
- **Necessary, NOT sufficient.** Nothing leaned byte at full power -- so the representation-artifact
  reading is WEAKENED -- but PHILOSOPHY is NOT ESTABLISHED: the verdict rests SOLELY on K3b (pre-flagged
  as able to lean modeling for trivial flexibility reasons; twin 0.88 is consistent with
  representation-invariance), while K2b (the actual C-blindness probe) was inconclusive. A 17/20 that does
  not round to 18/20 is not narrated as a near-win.
- **I_C diagnostic (pre-registered, read-only) -- REJECTED.** A pre-committed hypothesis (K2b's
  instability tracks coalition property C, so the 3 negative-Delta seeds would be high-I_C) was tested
  against the committed plug-in I_C method on the locked seeds: the negative-Delta seeds rank [12, 1, 17]
  of 20 (scattered, mean rank 10.0 ~ random; 7008 is the LOWEST-I_C seed of all 20), Spearman(Delta, I_C)
  = -0.25 (below |0.4|, n.s. at n=20). Property-dependent-representation REJECTED -> the K2b near-miss is
  genuine NOISE; INCONCLUSIVE-as-noise stands.
- **Control (e)(i) (hold ONE encoding constant across all five proxies) stays PENDING / UNJUDGED**, with
  its recorded distortion: K1/K5 cannot go categorical-native, so (e)(i) forces the modeling proxies onto
  the byte stream -- it probes the same axis from the opposite anchor.

### 8.4 v0.7 program reframe (epistemics, not results; commit `bbd081c`, 2026-06-24)

A pre-registered, failure-SURFACED (not failure-driven-to-dodge) reframe with an anti-post-hoc gate: the
two grounds for demoting R2 each hold INDEPENDENT of the D1 outcome.

- **D1's role -> ESTIMATOR COVERAGE-CALIBRATION** vs known ground truth (the D1 `R2>0.6` commitment is
  SUPERSEDED IN STATUS -- number kept, not deleted -- resolving the prior CHARACTERIZED-vs-locked-threshold
  contradiction in favor of CHARACTERIZED). The finding is DIFFERENTIAL coverage with K5 (parsing) MOST
  COMPLETE -- ASYMMETRIC, not compositional: K5 the widest aperture (A,B,C,D), the modeling trio gapped to
  {A,D}, compression to {A,C}, A universal; the ensemble-recovers-all is CARRIED BY K5 (so "no single K
  recovers all" is FALSE and dropped). Actionable for D2/D3 (no ground truth): weight K5-type PARSING as
  the widest aperture, treat the modeling trio + compression as SPECIALIZED / CONFIRMATORY. The
  calibration ITSELF is provisional (single seed 7000, 16% of locked T, C seed-variable).
- **R2 -> DIAGNOSTIC.** Corroborating on convergence, NON-FALSIFYING on divergence. The COVERAGE CEILING:
  induced w is constitutively (substrate x K), so cross-estimator agreement certifies only shared-coverage
  structure and divergence outside it is ambiguous; the metrology analogy (independent instruments
  certifying a real observable) FAILS because K1-K5 are different FUNCTIONALS, not measurements of one
  observable. This holds even on a PASS (which would certify only the least-common-denominator). The
  0.6/0.4 numbers are KEPT as a convergence flag; the grid is intact and still runs.
- **R1 + the v0.6.2 functional win -> PRIMARY.** Falsifiability is RELOCATED (not removed) to R1/R3
  (functional), a HEAVIER commitment. R1 SPEC GUARD (locked NOW, before R1 is built): functional
  convergence = PER-ESTIMATOR functional validity AGGREGATED, NOT cross-estimator agreement on
  predictions. R1 is still per-estimator coverage-limited (K2 can't see C -> its w can't predict C-driven
  persistence); it escapes the ceiling ONLY by not requiring cross-estimator AGREEMENT -- operationalizing
  R1 as prediction-agreement would rebuild R2 in a functional costume.
- **Eight-cell outcome matrix -> RE-DERIVATION pending.** Under R2-as-diagnostic (R2 no longer a pass/fail
  axis) the Metacoherence Sec 8.3-8.4 matrix needs re-derivation (plausibly R1/R3 as the pass/fail axes,
  R2 as a coverage annotation); the source-locked 51-cell Bonferroni accounting carries over but its
  falsification budget now concentrates on R1/R3. Capstone-pending, NOT resolved here.

### 8.5 v0.7.1 R1 (persistence) -- RESULT: D1 R1 = calibration (necessary-not-sufficient, mechanism-confounded)

**Built + run + closed** (`90a3211` pre-reg -> `346f700` build-time amendment -> `95d85ff` apparatus + finding -> `7963eb5` closer). Authoritative record: `pre_registration.md`, the 2026-06-24 v0.7.1 R1 entries.

**Substrate finding (read-only, verified by line number).** A re-read of the locked D1 generator found the regime path is EMISSION-INDEPENDENT: `_sojourn_states` draws pure negbinom dwells + uniform jumps, fixed BEFORE the emission loop; drift is post-hoc and feeds only f4. So the Metacoherence Sec 5.4 drift->transition coupling is NOT instantiated, and D1 "persistence" reduces to REGIME-INFERENCE structure, not D-driven survival. Consequence: the source's `tau_rec` regime-decoder is DEFERRED (no Viterbi in-repo; HSMM not HMM), and the PRIMARY measure is the DECODER-FREE sustained marginal-relative log-likelihood-cost MAGNITUDE; the perturbation is generative + RNG-preserving (states + non-target features bit-identical), with f1/f3 recorded per-state-uniform (condition on own latents, marginalize cross-feature relations).

**Apparatus validated (the calibration deliverable).** `cit/persistence_d1.py` (Section 3.2); 11 fast tests. The validation gate PASSED: distractors ~0 (the marginal-relative computation correctly refuses the skewed Zipf/low-freq marginals), and the relational B / coalitional C are per-feature-invisible by design.

**The D-led finding, disambiguated at 20 seeds.** Cost ordering: f4(D) ~ 1.72, f0(A) ~ 0.28, B/C/distractors ~0; D leads A on 20/20 seeds, ratio ~6.7. A pre-registered seed-variability diagnostic (reads fixed before the numbers) = MIXED: the measure is information-sensitive WITHIN a property (Spearman(A_cost, I_A) = +0.835) AND concentration-biased ACROSS (I_A ~ I_D yet D costs ~6.7x because its per-step emission is sharper). NOT "peakedness not information."

**Mechanism-confound (the partial proxy d-matrix).** Cheap cells only (timing-justified: K4 x A1 ~100 min / 20 seeds, K3/K5 worse; the full grid + A2 deferred -- predictable, confounded, slow): K1xA1/A3 d = -0.386 FAIL (D=f4 in K1's high-w on 0/20 seeds -- K1 misses D); K2xA1/A3 d = +0.986 PASS (D in high-w on 20/20). So "passing R1 on D1" == "weighting the sharp feature D," coinciding with the persistence-designated feature for the CONCENTRATION reason, NOT persistence-relevance. D1 R1 is therefore necessary-not-sufficient AND MECHANISM-CONFOUNDED: it validates the apparatus + confirms coverage, NOT that `w` tracks persistence.

**STANDING D2/D3 dependency.** The magnitude measure is concentration-sensitive; the cross-property confound bites ONLY under heterogeneous emission concentration. Resolution before D2/D3 is CONDITIONAL: check emission-concentration HOMOGENEITY first; if comparable, the measure is fine as-is; if heterogeneous, info-normalize. Parked, pre-registered.

### 8.6 D2 (Pfam) R1 -- PRE-REGISTERED (`df025a3`; design only, NOT built)

Pre-registers R1 for D2 (Pfam, CC0) -- the LOAD-BEARING R1 domain (R1 = PRIMARY). Authoritative: `pre_registration.md`, the 2026-06-24 D2 entry. Transcribed from Meta-coherence Sec 6 with Benjamin's (c)/(d) rulings locked:

- **Substrate (6.1):** 20-30 Pfam families, 4-axis EQUAL stratification (ortholog depth `>= 500` @90% redundancy; structural CATH/SCOP all-a / all-b / a-b / a+b; GO functional enzymatic / structural / regulatory / signaling; ~half catalytic). The exact count + family list are FLAGGED for the data survey.
- **Stream (6.2):** ortholog-indexed 21-letter (20 aa + gap) position-by-ortholog matrices; the 5x3 grid runs unchanged; the R1 bootstrap resamples ORTHOLOGS (not time).
- **R1 measure (6.3, LOCKED):** per-position mutation tolerance = ML PER-SITE RATE (Rate4Site-style, CONTINUOUS -- not integer substitution counts, which tie/degrade the Spearman; independent-contrasts rejected as a continuous-trait category mismatch); R1 = per-family Spearman(`w`, INVERSE tolerance), ortholog-resampling bootstrap, cross-family aggregate vs the Sec 8 threshold. EMPIRICAL, not likelihood-based -> the D1 concentration confound does NOT carry. DETERMINISM DEPARTURE: D2/D3 use SOFTWARE-PINNED reproducibility (MSA release + tree-inference + rate tool + versions + params + pinned per-family tree), NOT bit-exact -- a recorded scope change for D2/D3 only (D1 / v0.6 stay bit-exact).
- **Conservation-tautology confound check (load-bearing; pre-registered FIRST):** inverse substitution tolerance ~ column conservation / low entropy, which a compression `w` may track definitionally -> R1 risks the "does `w` detect low-entropy columns" near-tautology. PRIMARY control = ENTROPY-BASELINE CONTRAST (does `w`'s Spearman exceed a pure column-entropy baseline-`w` by a pre-registered MARGIN -- the project's native baseline-relative idiom; margin FLAGGED for Benjamin); CORROBORATING = conservation-stratified within-bin R1; partial Spearman dropped; CONCORDANCE RULE (surviving only if BOTH clear; disagreement = CONFOUND-AMBIGUOUS, a named outcome); DISCONFIRMER (collapse to baseline => conservation-confounded, "compressors find conserved columns," NOT functional-persistence evidence).
- **Pfam = comparison compression, NOT adjudicator (4.4 / 6.4):** three SEPARATED uses -- M5 partition (documented catalytic/structural residues), R1 measure (substitution tolerance), Pfam conservation scores (a parallel R2 compression); `w`-vs-Pfam divergence is an informative finding, never an induced-`w` failure.
- **M5 partition (6.4):** coherence-bearing = catalytic + fold-defining + top-conservation-quintile; noise = surface-exposed non-functional + bottom-conservation-quintile. Documented biology, fixed at pre-reg.
- **Carried:** the R1 spec guard; R1 PRIMARY; R2 diagnostic; R3 (6.5: in-silico relaxed-selection vs BLOSUM-equivalence-class relabeling) deferred to its own step.

Two numbers FLAGGED for Benjamin / the data survey: the entropy-baseline MARGIN and the FAMILY COUNT + stratification list. **SUPERSEDED-IN-STATUS by Section 8.7** -- the survey RAN and the design then advanced through a conservation-tautology rework + a framing-S premise check + a coevolution-coupling pilot; the entropy-baseline / family-count numbers are PARKED behind the now-open edge->node question.

### 8.7 D2 beta-line -- survey + framing-S EMPTY + coupling pilot (intermediate) + B' FAIL -> edge->node escalation (pre-reg `4d7a7c6`..`3042fe2`)

The D2 build did NOT proceed to the locked R1 grid (8.6); a chain of PRE-REGISTERED adversarial checks redirected it, and it is now HELD on an open structural question. Authoritative: `pre_registration.md` 2026-06-24 D2 entries (rework `4d7a7c6`, resolution `b528a04`, dual-transposition redesign `84d5787`, coupling-pilot + B' pre-reg `3042fe2`); apparatus `scripts/pilot_d2_coupling.py` + `scripts/pilot_d2_bprime.py`; all pilot data gitignored. Pins: InterPro 109.0; PDB `1djc`; IQ-TREE 3.1.2 site rates as the Rate4Site-style stand-in (the phylo-tool pin is still open); N=2000, seed 0; 90%-redundancy filter skipped for the pilot.

- **Survey (API-only):** enumerated 30134 Pfam entries -> 27961 domain/family candidates; M-CSA-seeded catalytic axis -> 274 confirmed-catalytic families -> 253 with `alignment:full >= 500` (CATH folds balanced); non-catalytic half GO-seeded + THIN. `candidate_pool.tsv` = 271 families (gitignored).
- **Pre-reg amendments (rework/resolution/redesign):** the entropy-baseline control was PROMOTED from R1-only to the PRIMARY gate across R1 + M5; ortholog ordering pinned (fixed/UniProt-acc -> then a PINNED RANDOM PERMUTATION; phylo-order REJECTED for circularity with the phylo-derived target); subsample-to-N locked; family selection re-oriented to add a coevolution/contact axis; a dual-transposition pilot (framing S vs framing P) pre-registered.
- **Framing-S PREMISE CHECK (PF13354; the load-bearing finding):** the locked marginal-relative K1-K5 + A1, on a real Pfam alignment (2000 orthologs x 248 positions), produce ESSENTIALLY FLAT per-position `w` -- K2/K3 PERFECTLY flat (std 0), K1/K4 near-flat; NO proxy beats the column-entropy baseline (the entropy-baseline gate would reject ALL); the conservation-tautology premise is largely FALSE for these proxies -- they do NOT track conservation, they are EMPTY. Mechanism: A1 single-position LOO over ~248 positions barely moves the (~0) marginal-relative coherence -> rho~0 -> w~0.5. (K5 infeasible at N=2000: 673 s/eval.)
- **DECISION (Benjamin):** D2 coherence = cross-POSITION COUPLING (coevolution), NOT per-site conservation. Establish the beta SIGNAL exists before redesigning the KxA instrument.
- **Coupling pilot (PF13354; contacts + MIp as COMPARISON-COMPRESSIONS, Sec 6.4 idiom, NOT an oracle):** Meff 1522/2000; 244/248 cols -> `1djc:A`; 644 contacts (Cb-Cb < 8A, |i-j| >= 5); APC-corrected MIp. A (top-L MIp PAIR precision 0.131 vs base 0.022 vs conservation-product 0.016) PASS; C (Spearman(s_i, conservation) -0.338; vs inv-tol +0.016) PASS; B (Spearman(s_i, contact_degree) +0.101 vs conservation +0.430) FAIL. VERDICT = INTERMEDIATE: the pairwise coevolution signal is REAL, strong, conservation-INDEPENDENT (A, C), but the per-position SUM s_i is a WEAK contact predictor (B).
- **B' (pre-registered, burial-controlled edge->node):** node aggregations s_max / s_top5 / s_cnt from the existing MIp; burial = `HSExposureCB` (EXP_HSE_B_U) on `1djc:A`; partial Spearman(., contact_degree | burial) vs conservation's. RESULT = **B'-FAIL**: the burial confound was REAL (contact_degree ~ burial +0.784; conservation's contact prediction drops +0.430 -> +0.143 once burial-controlled), but NO aggregation beats conservation's burial-controlled partial (s_max +0.020, s_top5 +0.026, s_cnt -0.012, all < +0.143). The edge->node projection LOSES the signal.
- **ESCALATION (the pre-registered B'-FAIL decision; OPEN for Benjamin):** coevolution is EDGE-valued; CIT induced-`w` is NODE-valued (Sec 6.2 per-position `w`). No tested node-projection recovers per-position contact structure beyond burial-confounded conservation -> Sec 6.2's per-position-w construction is UNDER STRAIN for D2. beta stays a CANDIDATE, NOT locked into D2. The open question: a faithful edge->node projection (an untried aggregation / a graph-centrality on the MIp matrix) vs an intrinsically-EDGE-valued `w` (a departure from Sec 6.2) vs D2 cannot realize beta at per-position granularity. The D2 KxA grid, the family lock, and the R1/M5/R2 production runs are HELD pending the ruling.
- **B2 RESULT -- node-valued w SURVIVES (NARROWLY; `scripts/pilot_d2_b2.py`):** B2 pre-registered three GRAPH-STRUCTURAL node projections of the MIp graph (W = max(APC-MIp, 0), diag 0; reuses the MIp `.npz`, no recompute): g_eig (eigenvector centrality), g_pr (PageRank, d=0.85), g_topL (top-L-pair node degree = the A->node bridge); same burial control as B'. RESULT = **B2-PASS via g_pr**: PageRank's burial-controlled partial Spearman(., contact_degree | burial) = +0.151 BEATS conservation's +0.143 (g_eig +0.092, g_topL +0.052 both FAIL). So Sec 6.2's NODE-VALUED `w` SURVIVES -- the edge-valued branch A is NOT forced. TWO CAVEATS: (i) the pass is RAZOR-THIN (+0.008 over conservation) on a SINGLE family -- the pre-registered rule REQUIRES confirmation on >= 1 more coevolution-rich family BEFORE any node-valued lock; (ii) the recorded (non-gating) prediction was INVERTED -- g_topL (the predicted candidate) FAILED while global PageRank flow PASSED, so the surviving node signal is graph-FLOW centrality, NOT top-L contact-pair membership. NEXT: replicate B2 on >= 1 more family -> if it holds, node-valued joint-proxy design; if not, edge-valued `w` (branch A) + the corpus-admissibility check. The D2 grid / family-lock / R1-M5-R2 runs stay HELD.
- **SECOND-FAMILY REPLICATION + EDGE-M5 RESULT (`scripts/run_d2_family2.py`; pre-reg `b8de3f1` -> result 2026-06-25):** discharges the B2 confirm-clause on PF00026 (Asp / 4y9w:A; pure all-b aspartic protease; lowest-accession family under the outcome-independent rule with a >=150-col domain floor that excluded the literal hit PF00024/PAN_1 as a weakly-catalytic disulfide module). Matrix-build recipe pinned BIT-EXACT to PF13354 (verified rebuild). L=312, coverage 293/312, Meff 1438.6, 811 contacts. **EDGE GENERALIZES:** check A top-L MIp precision 0.160 vs base 0.019 PASS; edge-M5 PASS -- AUROC MIp 0.802 (CI 0.789-0.814) > conservation-product 0.442 AND > burial-product 0.685, LONG-RANGE 0.794 > 0.700 (MIp beats BOTH controls incl. burial, even long-range). The PF13354 edge-M5 FOLD-IN: MIp 0.698 BEATS conservation (0.419) but LOSES to burial (0.716) -> the edge-vs-burial margin is FAMILY-DEPENDENT (loses on small a-b/a+b PF13354, wins on larger all-b PF00026). **NODE does NOT clear the HARDENED bar:** refs entropy-conservation +0.091 / phylo-inv-tol +0.134; B' aggregations (+0.099/+0.118/+0.113) beat the WEAKER entropy ref (so B' did NOT fail here, unlike PF13354) but none beat phylo; B2 g_eig -0.032 / g_pr +0.127 / g_topL +0.152; the HARDENED g_pr test = margin vs phylo -0.007 (CI -0.154,+0.129 INCLUDES 0) -> NOT ROBUST; the B2 PF13354 g_pr pass did NOT replicate and the winning projection is UNSTABLE (g_pr PF13354 / g_topL PF00026). **DECISION-RULE MAPPING (MIXED -> HELD):** EDGE GENERALIZES = YES; NODE robust pass = NO; strict 'node-fail generalizes' = NO (only because B' beat the weaker entropy ref); the HARDENED phylo bar -- pre-registered AS the bar -- FAILS. So edge is DE-RISKED, node is NOT; the branch (retire-node + relational/edge-valued build vs node-survives) is HELD for Benjamin. HARD STOP TWO families; family list NOT locked; no build started.
- **RELATIONAL BUILD step 1 -- BRANCH ADJUDICATED + R2-EDGE premise RAN + PASSED (`scripts/r2_edge.py`; pre-reg `e3e0458` -> result 2026-06-25):** Benjamin RETIRED node-valued `w` (fails the hardened phylo bar both families) and ADOPTED edge-valued `w` (corpus-aligned: coevolutionary coupling is a DENSE entangled field, not a sparse direct-edge graph; DCA/inverse-covariance is the PEARLIAN cut the corpus deconstructs, EXCLUDED as a convergence partner). Edge-`w` formalism = CIT per-symbol `w` on the JOINT pair-symbol over the product alphabet (formal-admissibility check -- Shannon-recovery/coarse-graining/monotonicity -- flagged separate, not gating). R2-EDGE tests convergence across CIT's OWN distinct DENSE paradigms: K_MI = APC-MIp (Shannon plug-in, reused) vs K_comp = a KT/MDL compression edge coupling (joint-vs-independent codelength on reweighted effective counts; the 441-symbol-joint complexity penalty makes it algorithmically distinct -- validated +1674 bits coupled / -27 independent). RESULT = **R2-EDGE PASS BOTH families**: (i) long-range Spearman(K_MI,K_comp) +0.542 (PF13354) / +0.745 (PF00026), both >=0.5; (ii) top-L Jaccard 0.15/0.24 (modest -- expected for genuinely distinct estimators); (iii) CONSENSUS edges (top-L in both) beat each estimator alone on contact precision (0.242 vs 0.131/0.086; 0.214 vs 0.160/0.150, ~11x base) -- substrate-informative; (iv) the convergence SURVIVES and in fact STRENGTHENS under the conservation-product + burial-product control (partial +0.651 / +0.852 vs raw +0.583 / +0.775), so it is NOT the agree-on-conserved/buried-pairs null. The edge-valued direction is supported by cross-paradigm convergence with the burial confound controlled. Two families, NO grid, NO lock; MIp-high non-contact pairs logged as an R1-edge question (allostery/long-range), NOT noise. NEXT relational component = Benjamin's call.
- **RELATIONAL BUILD step 2 -- edge-w FORMAL-ADMISSIBILITY RAN + PASSED-AS-CODED, RETRACTED by step 3 (`scripts/admissibility_edge.py`; pre-reg `4354ed3` -> result 2026-06-25; ADVERSARIALLY VERIFIED by a 6-agent workflow):** [RETRACTED -- the PASS was TAUTOLOGICAL (check B hardcoded np.ones) and verified the WRONG object (the 441-joint edge-w, which COLLAPSES to single-source node-w); superseded by the step-3 bullet below + the corrected I_w_rel. Original record kept for the audit trail.] a VERIFICATION (pre-fixed criteria) that edge-w = CIT per-symbol w on the joint pair-symbol is an EXTENSION of the H_w/I_w machinery, not a fork. RESULT = A-F ALL PASS, both families (PF13354, PF00026), both estimators (K_MI=APC-MIp, K_comp=KT/MDL): (A) boundedness w in [0,1] exact; (B) Shannon recovery at w=1 |dH|=|dI|=0.0; (C) coarse-graining (Dayhoff-6 + gap) Spearman K_MI 0.966/0.980, K_comp 0.865/0.845, all >=0.7; (D) monotonicity 0 inversions; (E) within-class relabel invariance =1.0; (F) 100-bootstrap stability K_MI 0.993/0.993, K_comp 0.991/0.986, all >=0.8. The pre-registered KEY RISK (pair-features OVERLAP, each position in L-1 pairs -> not a partition) broke NONE of the formal properties. VERIFICATION: 6 from-scratch verifiers all CONFIRM, every number reproduced clean-room; estimators() APC-MIp BIT-EXACT to the saved baseline (diff 0.0); matmul joint-count trick correct to <=5e-13; no weakened threshold; no REFUTE. TWO HONEST FOLLOW-UPS flagged (NOT folded into the PASS): (i) check B is ALGEBRAICALLY TAUTOLOGICAL as-coded (hardcodes w=1 inline; does NOT exercise canonical cit/information.py -- recovery confirmed independently against those funcs to ~1e-16) AND the I_w weighting convention (edge-w over 441 joint product-alphabet symbols vs canonical I_w over the 21-symbol source marginal) is invisible at w=1 -> an OPEN formal point: WHERE the edge weight attaches in I_w(X_i;X_j); (ii) the overlap / partition-of-unity ACCOUNTING is NOT probed by A-F (all treat eligible pairs as a flat independent list) -> LEFT OPEN as the next adjudication. Minor: a defensible pin deviation (full-MIp recomputed as the E/F reference, bit-exact to saved, saved untouched) + one harmless dead line (admissibility_edge.py:125). VERDICT (RETRACTED by step 3): edge-w ADMISSIBLE-AS-EXTENSION for the formal properties tested -- BUT of the WRONG object (the 441-joint edge-w); see the step-3 bullet for the corrected verdict.
- **RELATIONAL BUILD step 3 -- RETRACT the joint-symbol edge-w + INSTALL the relational functional I_w_rel + STRESS-TEST (`scripts/relational_formalism_test.py`; pre-reg `017a7e4` -> result `046a596` 2026-06-25; foundations design/relational_formalism.md):** RETRACTS the step-2 edge-w object AND its PASS. FOUR reasons: (1) the 441-joint edge-w COLLAPSES to single-source node-w on a merged node -- weights joint symbol-VALUES not the RELATION, does NOT vanish at independence (not relational, violates P2); (2) canonical I_w weights the 21-symbol SOURCE MARGINAL, so a 441-length weight fails _check_weights (not shape-admissible); (3) the corpus defines w ONLY single-source -- a real FORMAL GAP; (4) the step-2 PASS was FALSE COMFORT (check B hardcoded np.ones; E/F same-code recompute; pair-overlap never probed). CORRECTED OBJECT weights the RELATION as a SCALAR: I_w_rel = sum_{(i,j) in E} w(i,j) I(X_i;X_j) over the DENSE complete graph (P3), with I = RAW pairwise MI via CANONICAL cit/information.py at w=ones (clean Shannon boundary), w INDUCED from marginal-relative proxies (beta=4.0; the same formal/induced split single-source CIT uses); C_rel = I_w_rel/sum I in [0,1]; node-induced c_i with the EXACT HANDSHAKE sum_i c_i = 2 I_w_rel closing the previously-unprobed overlap. RESULT = **GAP CLOSED both families** (PF13354, PF00026): stress-test S1-S6 PASS -- (S1) REAL Shannon recovery via canonical + non-trivial weight response (|I_w_rel-sum I|<=3.6e-12 at w=1, 4878-7498 bits off-boundary); (S2) non-collapse -- relational alpha=w*I ~ 0 at independence (alpha/beta ~ 0.001) vs the retracted merged-node beta=H(X_i,X_j) 1.3-2.0 bits; (S3) handshake exact (<=7e-12 at w=1/random/induced); (S4) monotonicity (0 inversions); (S5) boundedness (C_rel in [0,1], =1 at w=1); (S6) within-Dayhoff relabel-invariance (0.0); all via canonical, tested at w != 1. The two step-2 follow-ups DISCHARGED (441-vs-21 convention MOOT; I via canonical; overlap closed by the handshake). S7/S8 EVIDENCE (Benjamin rules, NOT decided): raw-I base favored (sum raw-I>=0 at 11440/14961 bits vs sum MIp NEGATIVE -300/-438, ~60% edges MIp<0 -> MIp base leaves [0,1]); sum-I normalizer favored (C_rel 0.57/0.59 in [0,1] vs /|E| 0.19-0.22 b/edge vs /max-I ~5100-7600 not in [0,1]). VERDICT: the corrected RELATIONAL object is ADMISSIBLE (formal GAP CLOSED); this REPLACES the retracted step-2 PASS. NEXT = Benjamin's call (rule c1 normalizer / c3 base / c-merge; or R1-edge / M5-edge / graded R3-edge / K_pred).
- **RELATIONAL BUILD steps 4-6 -- c3/c1 RULED + R1-EDGE (the PRIMARY signature) PILOT-PASS then NULL-FALSIFIED + pinv->OLS fix (apparatus `scripts/r1_edge.py` + `r1_edge_family3.py` + `r1_null_probe.py` + `select_third_family.py`; pre-reg/results `02c87f8`/`041927e`/`4eb6cba`, 2026-06-25; adversarially verified 3x):** STEP 4 RULED c3 = RAW I base (base/weight separation, foundation P7: raw information in the functional base, coherence in w) + c1 = sum-I normalizer; c-merge DEFERRED; beyond-background MIp / max(MIp,0) [c3-gamma] RETRACTED. R1-EDGE: does induced edge-w predict PHYLOGENY-CORRECTED coupling PERSISTENCE (= MEDIAN raw MI across K=8 phylo-INDEPENDENT subclades, the r1_edge tree-cut)? PILOT PASS on PF13354/PF00026 + a deterministic clean-tree THIRD family PF00348 (polyprenyl_synt, 8a7c:A @1.2A, K_eff=6 BALANCED max-clade 32% -- the antidote to PF00026's caterpillar; outcome-independent selection over candidate_pool.tsv, 27 skips recorded incl. PF00141 pathological-tree timeout): long-range SEPARATED partial(w, persistence | cons_i,cons_j,bur_i,bur_j) > 0 with position-block CI excluding 0, conservation-CLEAN on the load-bearing K_MI arm (PF00348 +0.298). STEP-6 NARROWINGS (verified): (i) sigma-induction w=sigma(beta z(C_hat)) is a RANK NO-OP -> every rank-based signature tests the ESTIMATOR, not the weight MAGNITUDES (the I_w_rel/C_rel functional stays empirically UNTESTED); (ii) an advisor 'K_comp~=MIp redundant, collapses to -0.095' premise was FALSE (the -0.095 was a beyond-marginal-target diagnostic; K_comp retains +0.43/+0.26/+0.40 beyond APC-MIp, +0.34/+0.18/+0.39 beyond RAW MI) -> RETRACTED. APPARATUS FIX: partial_sep + partial_multi pinv -> OLS-residual-on-ranks (robust to collinear covariates; the step-5 '+0.903 cons-null leak' was a pinv-under-collinearity artifact -> ~0; load-bearing cells unchanged). DECISIVE NULL-PROBE (the within-domain null every signal needs; 20 structured-noise surrogates x 3 families; adversarially verified 4-agent) = K_comp's beyond-raw-MI persistence is a MARGINAL-BIAS ARTIFACT on ALL 3 families: a surrogate that DESTROYS within-subclade coupling while PRESERVING marginals + subclade phylogeny reproduces/EXCEEDS the real partial (REAL +0.338/+0.175/+0.394 vs surrogate +0.274/+0.220/+0.463, z +6.26/-7.32/-11.71; PF00026/PF00348 REAL falls BELOW the null). MECHANISM: Spearman(raw MI, K_comp) = +0.996/+0.992/+0.993 -- K_comp is a NEAR-MONOTONE transform of raw MI, NOT a genuinely distinct paradigm; the 'beyond-MI residual' is degenerate noise + a shared finite-sample MARGINAL-BIAS channel (persistence is dominated by the plug-in MI bias floor, which the raw-MI/cons/burial controls fail to absorb and K_comp tracks). This REFINES R2-edge step-1: 'two genuinely distinct DENSE paradigms converge' is REAL convergence but is APC-MIp vs near-raw-MI = the SAME Shannon-plug-in paradigm differing by the APC correction, NOT two philosophies. SURVIVES (untouched): MIp coevolution PERSISTS across phylo-independent subclades, conservation/burial-clean -- a genuine gain over node-w's conservation-circularity, but the FIELD's standard MI coevolution signal re-described, NOT a compression-specific coherence signal beyond MI. CONCLUSION (the pre-registered fork, on DATA): CONCEDE the beyond-MI compression finding as within-domain noise; the decisive test of the multi-proxy coherence construct is CROSS-DISJOINT-DOMAIN TRANSFER with a structured-noise null -- NOT another within-domain proxy (K_pred WRONG: within one domain everything collapses to MIp + shared bias). A clean falsification on data. NEXT = Benjamin's call (cross-domain transfer / D3). M5-R2 / grid / family-lock runs stay HELD.
- **RELATIONAL BUILD step 7 -- D2 LINE CLOSED AS A FALSIFICATION: K_comp = affine(raw MI) THEOREM; R2-edge convergence ILLUSORY; arc ledger (apparatus `scripts/r1_null_probe.py`; pre-reg/result 2026-06-25; 2-agent adversarial verify -- bit-exact from-scratch reimplementation + adversarial break-search):** the step-6 mechanism is now an ALGEBRAIC THEOREM. (1) K_comp = N_eff*(raw MI) + (pen_i + pen_j - pen_ij) = N_eff*(raw MI) - KT_penalty, an EXACT identity verified to <=7e-12 per pair (slope b == N_eff because both MI and codelength are in bits, the two ln2 factors cancel; OLS R^2 0.9937/0.9866/0.9880; slope/N_eff 1.025/1.041/1.060; Spearman(rawMI,K_comp) +0.9966/+0.9926/+0.9930). K_comp is NOT a distinct estimator; the offset has only ~0.6% of K_comp's variance (and is itself MI-correlated via joint occupancy), so adding it lifts OLS R^2 to 0.99997. No subregime breaks the affine fit (top/bottom-decile-MI Spearman +0.98/+0.975). (2) PENALTY-MAGNITUDE CORRECTION (the one over-statement in the step-7 brief, fixed against data): the briefed '-200*log2 N' is the right SHAPE but ~3x too large -- it assumes the saturated 440-df asymptote (-2114/-2098/-2075), but the 21x21 joint is ~62% EMPTY (mean occupied 166/173/138 of 441), so KT charges only for the realized support; the net penalty scales with the effective-parameter count (occ_joint - occ_i - occ_j + 1) at -0.5*log2(N_eff)/param (Spearman -0.999 with the per-pair penalty), landing at the empirical intercept -735/-722/-721, NOT the asymptote. (3) RE-RETRACT step-6 narrowing-(ii): the '+0.43 beyond APC-MIp' (the step-6 'K_comp distinct' evidence) was JUST the APC background (K_comp ~= raw MI; APC-MIp = raw MI - background); the '+0.34 beyond RAW MI' was the marginal-bias artifact -- BOTH step-6 framings (redundant AND distinct) are superseded: ONE Shannon-plug-in family. (4) R2-edge step-1 convergence ILLUSORY: the headline long-range Spearman(K_MI,K_comp) +0.542/+0.745 == Spearman(rawMI, rawMI-APC) (Spearman(K_MI,rawMI) +0.555/+0.786 ~= the headline; Spearman(K_comp,rawMI) +0.996/+0.992); removing raw MI from BOTH arms leaves a NEGATIVE residual correlation -0.147/-0.445 -> there is NO second paradigm underneath the shared raw MI (the contact-precision gain survives as an APC-vs-no-APC ensembling effect, not cross-paradigm corroboration). (5) ANNOTATE foundation P4 ('compression distinct from information'): UNSUPPORTED in D2 -- the KT/MDL edge proxy collapses to MI for a fixed finite alphabet, so the D2 estimator selection was MIS-SPECIFIED for a coherence-beyond-MI test; P4 may still hold for D1's zstd/Lempel-LZ proxies (NOT analytic MI), untested by an MI-independent estimator in D2. ARC LEDGER (D2 relational line, final) -- FALSIFIED/illusory: R2-edge cross-paradigm convergence, K_comp-as-distinct, P4-in-D2, any coherence-beyond-MI in proteins. SURVIVES: the relational FORMALISM (I_w_rel/handshake/Shannon-recovery admissible, a T2 result -- but sigma-induction is a rank no-op so the weight MAGNITUDES remain UNTESTED); the node-w falsification; M5 standard-MI->contact AUROC ~0.80; R1 deflated ('MIp coevolution replicates across phylo-independent subclades, conservation-clean' = the field's standard pairwise-MI coevolution signal re-described). NET: D2 recovered the field's pairwise-MI coevolution construct and NOTHING beyond it -- a clean 'vulnerable in the right way' FALSIFICATION; the WITHIN-DOMAIN protein program is EXHAUSTED as a coherence test. The non-circular claim (metacoherence = a TRANSMISSIBLE pattern across DISJOINT-prior domains, a property of the MAP between datasets) is untouched and is the next test. **v0.7.2 D2 relational line CLOSED; v0.7.3 OPENED = cross-domain transfer DESIGN DRAFT (`design/cross_domain_transfer.md`; OPEN -- architecture / domain-pair / 'what counts as transmit' / the multi-scale dependency all pending Benjamin + advisor; NO build, NO data, NO lock).**

---

## 9. Weight admissibility (M-conditions) -- the principled-quantity layer

The capacity/compression theorems need only `w in [0,1]`, finite alphabet, and `w` a fixed
per-symbol function (`w=1` recovers Shannon). The DISCIPLINE on induced weights is the
M-condition layer (from `formal 3.docx` = JAMFFO-3, extended in `Meta-coherence.docx`):

- **M1** boundedness + monotonicity in `rho` (rho up => w not down). [repo: `w=sigma(beta*rho)`]
- **M2** coherence-consistency under coarse-graining (no relevance-order flips under benign regrouping).
- **M3** stability under recursive reuse (long-run contribution, not transient salience).
  [operationalized as R2 cross-replicate Spearman >= 0.7]
- **M4** empirical derivability without exogenous semantics (>=1 data->C->rho->w route).
- **M5** domain-translation invariance up to monotone transformation. [the cross-domain gate]
- **M6** (Metacoherence only) recursive-reinforcement compatibility.

"Within the admissible class, estimation may vary" -- which is exactly why cross-proxy
convergence is the test. The repo's induction (`induce.py`/`induce_multi.py`) implements the
M4 route: `rho(x) = E_t[C_t - C_t(-x)]` (mean LOO drop in proxy coherence), `w = sigma(beta*rho)`.

---

## 10. Source documents (the theory lives outside the repo)

Benjamin's OneDrive (supplied 2026-06-23). `w == kappa`, `H_w == H_kappa`.

| File | Content |
|------|---------|
| `.../UFAP/Research/cit formal.docx` | **CANONICAL** -- "Capacity and Compression Theorems" (JAMFFO-2). Full proofs: Capacity Thm 4.1, Selective Compression Thm 5.1, weighted AEP (App A.2), I_w properties P1-P3 + weighted DPI, Binary Coherence Channel fixture (Sec 6). The App A.2 soundness flag lives here. |
| `.../UFAP/Research/cit_formal_equations.tex` | clean LaTeX summary of the above theorems. |
| `.../UFAP/2026/cit engineering.docx` | Engineering Induced Coherence Weights -- empirical protocols, Selective Compression as the primary target, win-margin examples, benchmark toys. |
| `.../UFAP/2026/formal 3.docx` | Formal Foundation of Induced Coherence Weights (JAMFFO-3) -- M1-M5 admissibility. |
| `.../UFAP/2026/Meta-coherence.docx` | cross-domain (M1-M6, M5 gate, eight-cell matrix) -- the v0.7 source. |
| `.../UFAP/Research/Info.docx` | background; low relevance to the operational theorems. |

PhilPapers references are listed in README.md and `cit/information.py`. NOTE: the capacity
solver, the concavity result, and the practical streaming coder appear in NONE of these.

---

## 11. Open seams and known issues

- **Seam 1** -- `(K5,K2)` under A2 = 0.491. RESOLVED `(K5,K2)`-specific (Section 4.4); stays
  `xfail(strict=True)`. Do not "fix" silently.
- **App A.2 soundness flag** -- RESOLVED-NEGATIVE at v0.6.1 (Section 7.5(3)): Thm 5.1 is unsound for
  `w != 1` (both directions); `H_w` demoted to a measure, the coder rebuilt against `H(Z)`.
- **Stale `pyproject.toml` markers docstring** -- names only "K_5 LZ76", predates K3/K4 and
  the noise tests. Cosmetic; left as-is.
- **v0.6 program SHIPPED (v0.6.0 / 0.6.1 / 0.6.2, 2026-06-23); v0.7 line SHIPPED + tagged as `v0.7.1` (2026-06-24)** -- all locked + released. **v0.7.0 D1
  BUILT + record-corrected; the decoupling control BUILT + RUN; the v0.7 program REFRAMED; v0.7.1 R1 BUILT
  + RUN + CLOSED; D2 (Pfam) R1 PRE-REGISTERED** (commits `d9eb3b5`, `823928a`, `f1d1da3`, `7cca0c5`,
  `231fd94`, `8277bdb`, `3ea5c50`, `d840553`, `bbd081c`; v0.7.1 R1 `90a3211` / `346f700` / `95d85ff` /
  `7963eb5`; D2 pre-reg + docs `df025a3`). The decoupling control RAN -> verdict INCONCLUSIVE /
  necessary-not-sufficient (Section 8.3): K3b modeling-confident (20/20), K2b unstable (17/20); a read-only
  I_C diagnostic REJECTED property-dependence, so K2b's near-miss is genuine NOISE. v0.7 PROGRAM REFRAMED
  (Section 8.4): D1 = coverage-calibration (differential, K5 most complete, asymmetric not compositional);
  R2 = non-falsifying DIAGNOSTIC; R1 + the v0.6.2 functional win = PRIMARY (with the R1 spec guard);
  eight-cell matrix needs re-derivation. v0.7.1 R1 is BUILT + RUN + CLOSED as CALIBRATION (Section 8.5:
  necessary-not-sufficient + mechanism-confounded, D-led, partial d-matrix K1 FAILS / K2 PASSES); D2 (Pfam)
  R1 is PRE-REGISTERED (Section 8.6; ML per-site-rate tolerance + the conservation-tautology confound check;
  two numbers flagged for the data survey). The D2 BUILD (gated on the data survey), D3, v0.7.2 (R3), and the
  M5 + eight-cell capstone remain PLANNING until their own dated amendments.
- **Decoupling control (e)(i) -- PENDING / UNJUDGED.** Hold ONE encoding constant across all five proxies.
  Known distortion: K1/K5 cannot go categorical-native, so (e)(i) forces the modeling proxies onto the byte
  stream (the same axis from the opposite anchor). Not executed; the INCONCLUSIVE-as-noise verdict stands
  without it.
- **Sec 6 fixture erratum (2026-06-23)** -- `C_C(eps)=0.5(1+eps)` is the value at uniform input,
  not the capacity (true `C_C` is higher for eps<1; see Section 7.2). Author erratum flagged; does
  NOT affect Capacity Theorem 4.1.

---

## 12. Notation / glossary

| Symbol | Meaning |
|--------|---------|
| `w(x)` / `kappa(x)` | coherence weight in [0,1] (same object) |
| `H_w` / `H_kappa` | coherence-weighted entropy (same object) |
| `I_w(X;Y)` | coherence-weighted mutual information |
| `C_C` / `C_kappa` | coherence capacity = `max_{p(x)} I_w(X;Y)` |
| `rho(x)` | per-symbol/feature coherence contribution (centered ablation differential) |
| `C_hat` | scalar proxy coherence estimate in [0,1] |
| `K1..K5`, form B | the six proxies (Section 3.4) |
| `A1/A2/A3` | LOO / Shapley / correlation-cluster ablations |
| `T_w,eps^n` | weighted (coherence) typical set |
| DMC | discrete memoryless channel `p(y|x)` |
| Seam | a pre-registered near-miss (`xfail(strict=True)`), not a bug |

---

*End of spec. Update this file alongside `pre_registration.md` as v0.6-v0.7 amendments land.*
