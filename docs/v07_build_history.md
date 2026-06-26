# v0.7 build history archive (cold storage)

Narrative archive of the CLOSED v0.7 build lines, moved out of the always-loaded agent
memory to keep it lean. NOT authoritative -- the authoritative record is `pre_registration.md`
(the locked-commitment log) plus `CLAUDE.md` (current-state bullet), `README.md` (status table),
and `design/` (foundations + spec). This file preserves the session narrative + commit refs so
nothing is lost; consult it on demand. The LIVE path (v0.7.3 cross-domain transfer) lives in
agent memory `v07-build-state.md`, not here.

ASCII-only. Last synced 2026-06-25 (HEAD `7dbb5ac`).

---

## v0.7.0 / v0.7.1 -- the D1 INSTRUMENT-CALIBRATION tier (SHIPPED + TAGGED `v0.7.1`)

Released + tagged `v0.7.1` (annotated, GitHub Release = Latest; release commit `38ca714` bumped
`0.6.2 -> 0.7.1` across pyproject/CITATION/CLAUDE/spec/README, NO code change; README v0.7.1 row
tidied to the top + trimmed `c9b020e`; fast suite green 272). The release ships the D1
instrument-calibration tier explicitly, NOT cross-domain validation.

### What's built (D1 + metacoherence pipeline)
- D1 substrate: `cit/data/hsmm_d1.py` (3-state HSMM, mean dwell 200, dispersion r=6, T=50000,
  N_REPLICATES=20, 8 alphabet-8 features F0..F7; M5 partition {f0..f4} coherence / {f5..f7} noise;
  seeds 7000..7019).
- Categorical pipeline: `cit/proxies/categorical.py` (marginal-relative K1-K5, FEATURE-MAJOR
  bit-tight encoder, `SHUFFLE_SEED=0` K1/K5 time-shuffle baseline), `cit/ablations/categorical.py`
  (A1/A2/A3 uniform-over-A), `cit/induce_cat.py`.
- Metacoherence `cit/metacoherence.py`: R2 grid (`compute_cell`/`compute_grid`,
  `cross_philosophy_r2`, `recovered_properties`, `build_cross_tab`, `partition_diagnostic`,
  `GRID_ABLATION_SEED=123`) + decoupling metric (`crossing_delta`, `crossing_assignment`,
  `concordance_verdict`, `twin_spearman`, `decoupling_control_verdict`, `compute_decoupling_run`;
  `CROSSING_REFS`, `DECOUPLE_STABILITY_N=18`, `DECOUPLE_CONFIDENT=0.40`, `DECOUPLE_WEAK=0.10`,
  `DECOUPLE_PROXIES`; K3b/K2b in `compute_cell`).
- Crossings `cit/proxies/crossing.py` (K3b=`neural_prequential_byte_proxy`,
  K2b=`bigram_mdl_byte_proxy`). Drivers `scripts/run_metacoherence_grid.py`,
  `scripts/run_decoupling_control.py`. Artifact `results/decoupling_control/`.
- Tests added: test_metacoherence_d1 (13), test_categorical_proxies (35),
  test_categorical_ablations (8), test_metacoherence_r2 (8), test_crossing_proxies (6 fast + 1
  slow), test_decoupling_control (20 fast + 1 slow), test_r1_persistence (11).

### The v0.7 program REFRAME (`bbd081c`; epistemics, not results)
Anti-post-hoc gate held (the two grounds for demoting R2 are INDEPENDENT of the D1 outcome).
(1) D1's role = ESTIMATOR COVERAGE-CALIBRATION vs known ground truth (the D1 `R2>0.6` commitment
SUPERSEDED-IN-STATUS, number kept). Finding = DIFFERENTIAL coverage, K5 (parsing) MOST COMPLETE,
ASYMMETRIC not compositional: K5 widest {A,B,C,D}, modeling-trio {A,D}, compression {A,C}, A
universal; union-recovers-all is CARRIED BY K5 (so "no single K recovers all" is FALSE, dropped).
D2/D3 action: weight K5-type PARSING widest, trio + compression SPECIALIZED/CONFIRMATORY.
(2) R2 = DIAGNOSTIC -- corroborating on convergence, NON-FALSIFYING on divergence (coverage
ceiling: w is constitutively (substrate x K), so cross-extractor agreement certifies only
shared-coverage structure). 0.6/0.4 KEPT as a convergence flag, grid intact.
(3) R1 (persistence) + the v0.6.2 selective-compression functional win = PRIMARY; falsifiability
RELOCATED to R1/R3. R1 SPEC GUARD (locked): functional convergence = PER-ESTIMATOR functional
validity AGGREGATED, NOT cross-estimator AGREEMENT on predictions (else R2 returns in a functional
costume). Eight-cell matrix needs re-derivation under R2-as-diagnostic (capstone-pending).

### v0.7.1 R1 (persistence) -- BUILT + RUN + CLOSED as CALIBRATION
Source = Meta-coherence.docx (Sec 2.2 / 5.4 / 5.5 / 8.7 + App C.3). Evolution (all pre-reg'd,
append-only): pre-reg `90a3211` -> build-time amendment `346f700` (a read-only re-read found D1's
regime path is EMISSION-INDEPENDENT -- `_sojourn_states` pure negbinom dwells + uniform jumps,
drift post-hoc feeds only f4 -> the Sec 5.4 drift->transition coupling is NOT instantiated, so D1
persistence = regime-INFERENCE structure; tau_rec decoder DEFERRED, PRIMARY = decoder-free sustained
marginal-relative log-likelihood-cost MAGNITUDE) -> apparatus+finding `95d85ff` (`cit/persistence_d1.py`,
`stream_with_emission_dists` reproduces locked obs BIT-EXACT, `generate_perturbed_stream`,
`persistence_cost_table`, numpy `cohens_d` + B=1000 bootstrap, `validation_gate`, `compute_r1_run`) ->
closer `7963eb5`.
- FINDING (20 seeds, T=50000): cost ordering D-LED not A-dominated (f4(D)~1.72, f0(A)~0.28, rest ~0;
  D>A 20/20, ratio ~6.7). Seed-variability diagnostic MIXED: information-sensitive WITHIN a property
  (Spearman(A_cost,I_A)=+0.835) AND concentration-biased ACROSS (I_A~I_D yet D costs 6.7x because its
  emission is sharper).
- Partial proxy d-matrix (cheap cells K1/K2 x A1/A3; K3/K4/K5 + A2 deferred): K1 FAILS (d=-0.386,
  0/20) / K2 PASSES (d=+0.986, 20/20) -- the MECHANISM-CONFOUND made concrete (passing R1 on D1 ==
  weighting the sharp feature D, which coincides with the persistence-designated feature for the
  CONCENTRATION reason, not persistence-relevance).
- VERDICT: D1 R1 = necessary-not-sufficient AND MECHANISM-CONFOUNDED.
- STANDING D2/D3 dependency: the magnitude measure is concentration-sensitive; resolution is
  CONDITIONAL -- check emission-concentration HOMOGENEITY across the domain's features FIRST; if
  comparable, fine as-is; if heterogeneous, info-normalize.
- Locked R1 constants (additive, no prior VALUE changed): `PERTURB_ALPHA=0.3`, `PERTURB_ONSET=25000`,
  `PERTURB_SEED=0`, `R1_BOOTSTRAP_SEED=0`, `_EPS=1e-12`. `scripts/run_r1_persistence.py` not written
  (cheap grid inline); full grid (K3/K4/K5, A2) is a gated future run.

### Decoupling control -- RESULT (CLOSED, `d840553`)
Modeling-on-byte-stream crossing decoupling representation from coding philosophy on D1's A1 column;
full-T x 20 seeds, 20/20, 0 FAIL. VERDICT = INCONCLUSIVE, necessary-NOT-sufficient: K3b
modeling-confident (20/20, median +0.506); K2b UNSTABLE (17/20, misses 18/20 by one seed; median
+0.363, ci90 includes 0); twins K3b-K3 0.88 / K2b-K2 0.80. A read-only I_C diagnostic REJECTED a
property-dependent-representation explanation (Spearman(Delta,I_C) -0.25 n.s.) -> K2b near-miss is
genuine NOISE. Discipline: 17/20 STAYS unstable; never tune 18->17 to manufacture a verdict.

### Coverage map / recovery profiles (D1 A1, feature-major, T=8000 seed 7000; provisional)
K1 {A,C}; K2/K3/K4 {A,D}; K5 {A,B,C,D}; union {A,B,C,D} CARRIED BY K5; A universal. Single-feature
marginal-relative C (seed 7000): K2 A 0.09/D 0.21; K3(GRU) A 0.13/D 0.22; K4(HMM) A 0.21/D 0.24 +
partial C (f2,f3 0.052); distractors ~0. Perf at T=50000: K5 ~125s/call; K3b ~tens of min/seed
(~20h over 20 seeds); K3 ~30-60s; K4 ~minutes.

---

## v0.7.2 -- D2 (Pfam, CC0) relational line: CLOSED AS A FALSIFICATION (unreleased)

NET: D2 recovered the field's pairwise-MI coevolution construct and NOTHING beyond it -- a clean
"vulnerable in the right way" falsification; the within-domain protein program is EXHAUSTED as a
coherence test. The decisive test was relocated to CROSS-DISJOINT-DOMAIN TRANSFER (-> v0.7.3).

### Beta-line (node-valued w) pilot -> branch adjudication
Survey DONE (M-CSA-seeded, InterPro 109.0 pinned; 271-family pool; `data/pfam/` gitignored).
Outcome chain (rework `4d7a7c6` -> resolution `b528a04` -> redesign `84d5787` -> coupling-pilot+B'
`3042fe2`; apparatus `scripts/pilot_d2_coupling.py` + `pilot_d2_bprime.py` + `pilot_d2_b2.py`):
- FRAMING-S premise check (PF13354): the locked marginal-relative K1-K5 + A1 produce ESSENTIALLY
  FLAT per-position w (K2/K3 std 0; no proxy beats the column-entropy baseline) -> proxies EMPTY
  under framing S; conservation-tautology premise largely FALSE (they don't even track conservation).
- DECISION (Benjamin): D2 coherence = cross-POSITION COUPLING (coevolution), not per-site conservation.
- COUPLING PILOT (PF13354; contacts + MIp as comparison-compressions): A (top-L MIp pair precision
  0.131 vs base 0.022) PASS; C (Spearman(s_i,conservation) -0.338) PASS; B (s_i vs contact_degree
  +0.101 vs conservation +0.430) FAIL -> INTERMEDIATE (pairwise coevolution real + conservation-
  independent; per-position SUM weak).
- B' (burial-controlled edge->node): burial confound REAL (contact_degree~burial +0.784); no node
  aggregation beats conservation's burial-partial (+0.143) -> B'-FAIL (the edge->node projection
  loses the signal).
- B2 (graph-structural projections): g_pr (PageRank) partial +0.151 BEATS conservation +0.143
  (g_eig/g_topL fail) -> NODE-valued w survives NARROWLY (razor-thin +0.008, one family, prediction
  inverted).
- SECOND-FAMILY replication PF00026 (Asp/4y9w:A; `09e5849`; recipe bit-exact to PF13354): EDGE
  GENERALIZES (edge-M5 MIp-AUROC 0.80 beats conservation AND burial, even long-range) but NODE-valued
  w FAILS the phylo-hardened bar (g_pr margin vs phylo -0.007, CI includes 0; B2 did NOT replicate)
  -> Benjamin RETIRED node-valued w, ADOPTED EDGE-valued w (corpus-aligned dense field; DCA/inverse-
  covariance EXCLUDED as the Pearlian cut).

### Relational build (edge-valued w), steps 1-7
- STEP 1 (`b28aefe`, R2-EDGE premise): convergence of K_MI=APC-MIp (Shannon plug-in) vs K_comp=a
  KT/MDL compression edge coupling. PASS both families: long-range Spearman +0.542/+0.745, consensus
  edges beat each alone on contact precision (~11x base), convergence STRENGTHENS under
  conservation/burial control (partial +0.651/+0.852). Top-L Jaccard modest 0.15/0.24.
- STEP 2 (formal-admissibility) RETRACTED by step 3: verified the WRONG object (edge-w = CIT
  per-symbol w on the 441-joint pair-symbol, COLLAPSES to single-source node-w, weights joint VALUES
  not the RELATION) AND the PASS was TAUTOLOGICAL (check B hardcoded np.ones).
- STEP 3 (`017a7e4` pre-reg -> `046a596` RESULT; `scripts/relational_formalism_test.py`): INSTALL the
  corrected RELATIONAL functional `I_w_rel = sum_{(i,j)} w(i,j) I(X_i;X_j)` over the DENSE complete
  graph; I = raw pairwise MI via canonical `cit/information.py` at w=ones; w induced from marginal-
  relative proxies; `C_rel = I_w_rel/sum I in [0,1]`; node-induced c_i with exact HANDSHAKE
  `sum_i c_i = 2 I_w_rel`. GAP CLOSED both families (S1-S6 PASS at w!=1). S7/S8 evidence favors raw-I
  base + sum-I normalizer (sum MIp NEGATIVE, ~60% edges MIp<0). Foundations
  `design/relational_formalism.md` + `design/relational_edge_w.md`.
- STEP 4 (`02c87f8`): c3/c1 RULED -- BASE = raw I (foundation P7 base/weight separation), NORMALIZER
  = sum I; c-merge deferred; c3-gamma retracted.
- STEP 5 (`041927e`, R1-EDGE = primary signature): does induced edge-w predict phylogeny-corrected
  coupling PERSISTENCE (median raw MI across K=8 phylo-independent subclades)? PILOT PASS on 3
  families incl. the clean-tree PF00348 (8a7c:A @1.2A, K_eff=6 balanced; deterministic selection, 27
  skips; `scripts/select_third_family.py` + `r1_edge.py` + `r1_edge_family3.py`): long-range separated
  partial > 0, CI excluding 0, conservation-clean on the K_MI arm.
- STEP 6 (`4eb6cba` -> `c06545b`): narrowing (i) sigma-induction is a RANK NO-OP (signatures test the
  ESTIMATOR not the weight MAGNITUDES -- the I_w_rel/C_rel functional stays empirically UNTESTED);
  narrowing (ii) RETRACTED then RE-RETRACTED. Apparatus fix pinv->OLS-residual. DECISIVE structured-
  noise NULL-PROBE (`scripts/r1_null_probe.py`, adversarially verified): K_comp's beyond-raw-MI
  persistence is a MARGINAL-BIAS ARTIFACT on all 3 families (surrogate destroys coupling, preserves
  marginals+phylo, reproduces/exceeds real). Mechanism: Spearman(raw MI, K_comp) +0.99 -> near-
  monotone transform of raw MI, NOT a distinct paradigm.
- STEP 7 (`3c74238`, line CLOSED; 2-agent adversarial verify; `scripts/verify_kcomp_affine.py`):
  THEOREM `K_comp = N_eff*(raw MI) - KT_penalty`, an EXACT identity (<=7e-12; OLS R^2 0.99, slope/N_eff
  ~1.0-1.06, Spearman +0.99; the briefed -200*log2 N penalty CORRECTED to occupancy-set ~-720, the
  441-cell joint ~62% empty) -> K_comp NOT a distinct estimator. R2-edge convergence ILLUSORY (headline
  = Spearman(rawMI, rawMI-APC); residual after removing raw MI from BOTH arms NEGATIVE -0.15/-0.45).
  P4 ("compression distinct from information") UNSUPPORTED in D2 (MDL edge proxy collapses to MI for a
  fixed finite alphabet; may hold for D1 zstd/LZ).
- ARC LEDGER -- FALSIFIED/illusory: R2-edge convergence, K_comp-as-distinct, P4-in-D2, any coherence-
  beyond-MI in proteins. SURVIVES: the relational FORMALISM (admissible T2; weight magnitudes
  untested), the node-w falsification, M5 standard-MI->contact AUROC ~0.80, the deflated R1 (the
  field's standard subclade-replicated MI coevolution, conservation-clean).

### D2 R1 pre-registration (HELD -- `df025a3`; revived only if D2 resumes)
The load-bearing R1 domain locks (Benjamin's (c)/(d) rulings): (a) 20-30 4-axis-stratified families;
(b) ortholog-indexed 21-letter matrices, 5x3 grid, bootstrap resamples ORTHOLOGS; (c) per-position
tolerance = ML PER-SITE RATE (Rate4Site-style, continuous), R1 = per-family Spearman(w, INVERSE
tolerance), EMPIRICAL not likelihood (D1 concentration confound does NOT carry); software-pinned (not
bit-exact), scoped to D2/D3; (d) CONSERVATION-TAUTOLOGY confound check FIRST -- PRIMARY = entropy-
baseline contrast (w's Spearman must beat a column-entropy baseline by a pre-reg margin), concordance
rule, disconfirmer; (e) Pfam 3 roles separated, never adjudicator; (f) documented-biology M5
partition; (g) spec guard carried, R1 PRIMARY, R2 diagnostic, R3 deferred. FIVE numbers still FLAGGED
(Benjamin's call; recommended in brackets): R1 floor [+0.05 Spearman], M5 log-ratio floor [his call],
contact cutoff [8A Cb-Cb], subsample N [2000, range 1500-3000], family count [20-22]. D2 ACQUISITION
is API-only (InterPro REST; `data/pfam/` + `api_cache/` NEVER tracked; whole-DB downloads abandoned).
D2 grid / family-lock / M5-R2 runs stay HELD.

---

## Commit-chain index (v0.7)
- D1 build: `d9eb3b5`, `823928a`; record-correction `f1d1da3`.
- Decoupling: pre-reg `7cca0c5` .. RESULT `d840553`.
- Reframe `bbd081c`; docs `96b4563`.
- R1: pre-reg `90a3211` -> `346f700` -> `95d85ff` -> `7963eb5`.
- Release: `38ca714` (bump 0.6.2->0.7.1) + `c9b020e` (README tidy); tag `v0.7.1`.
- D2 R1 pre-reg `df025a3`; spec propagation `8b01955`; grounding+resume note `2c1537d`.
- D2 relational: rework `4d7a7c6` -> resolution `b528a04` -> redesign `84d5787` -> coupling-pilot+B'
  `3042fe2` -> B2 `ce27f57` -> second-family `09e5849` -> R2-edge `e3e0458`/`b28aefe` -> formal-admis
  `48d3131` (retracted) -> step3 `017a7e4`/`046a596` -> step4 `02c87f8` -> step5 `041927e` ->
  step6 `4eb6cba`/`c06545b` -> step7 falsification `3c74238`.
- v0.7.3 (cross-domain) chain: see `v07-build-state.md` (live) and `pre_registration.md`.

Authoritative records: `pre_registration.md` (locked commitments + all dated amendments),
`design/v06_v07_spec.md` (Sec 3.8 + Sec 8), `design/relational_edge_w.md`,
`design/relational_formalism.md`, `design/cross_domain_transfer.md`.
