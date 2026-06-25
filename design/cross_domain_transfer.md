# Cross-domain transfer -- DESIGN DRAFT (v0.7.3)

> **STATUS: DRAFT. OPEN. DECISIONS PENDING Benjamin + advisor.** Real-domain architecture / pair /
> transmission metric remain OPEN. UPDATED 2026-06-25 (step 1) with VALIDATED well-posedness findings
> (Sec 4: order-collapse generalization, the flow-object escape candidate, the corpus-gap correction;
> strengthened constraint 4; the R1-persistence hook) and a GATING first experiment -- D-cal, a synthetic
> transfer-machinery calibration (Sec 8), PRE-REGISTERED + RUN separately (pre_registration.md).
> Opened 2026-06-25 by the D2 (Pfam) relational FALSIFICATION (the within-domain protein program is
> exhausted as a coherence test: D2 recovered the field's pairwise-MI coevolution construct and nothing
> beyond it; K_comp = affine(raw MI) is a theorem; see pre_registration.md step-7 and
> design/relational_edge_w.md Sec 7). No real-domain data, no flow object, no lock. ASCII-only.

---

## 1. WHY (the standing rationale)

Within a single domain, CIT recovers that domain's EXISTING field construct (D2 proved it -- edge
coherence reduced to MI coevolution; the flat first-order measure collapsed to the field statistic).
That is the correct, honest outcome of a within-domain test, and it is NOT the claim under test.

The non-circular claim is METACOHERENCE: that coherence is a TRANSMISSIBLE pattern ACROSS domains
whose field-priors are DISJOINT (the domains share no field vocabulary, so no single field's construct
spans both). Crucially, metacoherence is NOT a property IN any one dataset -- it is a property of the
MAP / TRANSFER BETWEEN datasets. A within-domain measurement can never witness it (it can only
re-describe the local field). The test must live in the transfer.

---

## 2. FOUR NON-NEGOTIABLE CONSTRAINTS (each learned the hard way)

1. **DISJOINT field-priors.** The two domains share no field vocabulary, so no single field's construct
   spans both. More disjoint = stronger test. (A third single domain -- e.g. FOMC-as-a-third-field --
   is NOT this: it would just re-describe a third field's construct, exactly the D2 outcome again.)

2. **STRUCTURED-NOISE NULL.** Coherence must transmit across domains WHERE matched structured-but-
   arbitrary surrogate data does NOT. Without this, "transmission" reduces to "statistics-is-universal"
   = empty. This is THE requirement the protein null taught us; it is what falsifies. Every candidate
   architecture below must name a buildable surrogate that PRESERVES the domain's marginal/low-order
   structure while DESTROYING the putative coherence, and the transmission claim must beat that null.

3. **THE TEST IS THE TRANSFER -- never within-domain recovery.** Re-deriving a domain's own field
   statistic (MI coevolution in proteins, n-gram structure in text, ...) is re-description, not
   transfer. The evaluated quantity must be a property of A->B (or of an A,B-shared invariant), not of
   A alone or B alone.

4. **NO MI-COLLAPSE TRAP (STRENGTHENED -- full generic-statistic panel).** The coherence MEASURE must
   NOT be an analytic transform of ANY single generic statistic. This is the K_comp = affine(MI) lesson
   made into a pre-flight GATE -- and the order-collapse generalization (Sec 4.1) shows a single statistic
   is not enough to exclude: before any transmission claim, regress the chosen measure against the FULL
   PANEL {pairwise MI, total correlation, entropy rate, global compressibility, power-law / criticality
   exponent, support / fractal dimension} and CONFIRM it is non-affine (non-monotone) in EACH, with a
   SHARED surviving residual that is what transmits cross-domain. A measure affine in any one panel member
   transmits only that statistic. NOTE (validated): architecture B's "scale-free signature" (Sec 3) IS a
   generic-criticality statistic (a power-law/critical exponent) -- so it is the HIGHEST-collapse-risk
   candidate, NOT the safe lean; it must clear this gate before it is trusted.

---

## 3. CANDIDATE ARCHITECTURES (scope each for feasibility; do NOT pick)

**(A) WEIGHT-TRANSFER.** Learn the map from domain-A substrate-features -> induced coherence-weights;
apply that learned map to domain B; test whether it predicts B's coherence-bearing structure vs the
structured-noise null.
- *Hard part:* a SHARED / learned feature space that is not domain-specific (else the map is just an
  A-encoder). Risk: the shared feature space silently imports field priors, breaking constraint (1).
- *Feasibility:* needs a principled cross-domain feature embedding; the most ML-heavy option; the
  surrogate null is clean (apply the same learned map to A-surrogates and B-surrogates).

**(B) INVARIANT-MATCHING.** Compute a domain-INDEPENDENT coherence invariant on A and on B
INDEPENDENTLY (candidates: the curvature Delta^2 C; the C-spectrum; a scale-free recursive signature);
test whether the invariants MATCH across A,B where the surrogates do NOT.
- *Hard part:* defining an invariant that is genuinely domain-independent AND not a re-encoding of a
  generic statistic (constraint 4). The invariant should be a SHAPE/spectrum, not a scalar that any
  field already reports.
- *Feasibility:* the most tractable null structure (compute invariant on real-A, real-B, surrogate-A,
  surrogate-B; the claim is real-A ~ real-B AND both != surrogates). Best fit for the multi-scale
  signature (Sec 4). **REVISED (validated 2026-06-25): NOT the safe lean.** A "scale-free recursive
  signature" (curvature / C-spectrum / critical exponent) IS itself a generic-criticality statistic, so
  it is the HIGHEST-collapse-risk of the three (strengthened constraint 4) -- two domains can share a
  power-law exponent for entirely unrelated reasons. It is viable ONLY if the invariant is the
  coarse-graining-FLOW object (Sec 4.2), not a static spectral scalar. Benjamin/advisor rules (Sec 6).

**(C) DOMAIN-TRANSLATION phi (the spec's M5).** Construct phi: A -> B preserving coherence up to a
monotone transform; test induced-w compatibility under phi.
- *Hard part:* HARDEST -- constructing phi without importing the priors of either domain; phi itself can
  smuggle in a shared construct and manufacture the result.
- *Feasibility:* lowest unless phi is sharply constrained (e.g. phi fixed by a non-coherence criterion,
  then coherence-compatibility tested as an out-of-sample consequence).

---

## 4. THE DEEP OPEN PROBLEM (flagged prominently) -- and why "higher order" does not escape

Within each domain the FLAT FIRST-ORDER measure reduces to the field statistic (D2: -> MI; and any flat
pairwise measure on a symbol stream -> co-occurrence MI). So transmitting the flat measure would be
transmitting the generic statistic -- "statistics is universal," the empty result constraint (2) guards
against.

### 4.1 ORDER-COLLAPSE GENERALIZATION (VALIDATED 2026-06-25; 2 verifier agents + corpus audit)

The K_comp = N*MI + penalty theorem (step 7) is term-for-term GENERAL: the KT codelength of a k-WAY
joint = N*(order-k information) + sparsity penalty (the same L_KT(c) = N*Hhat(c) + pen(c) expansion
applied to the k-way contingency table). Concretely, an order-k compression coupling
[ sum_i L_KT(marg_i) - L_KT(joint_k) ] = N*TC_k + net_penalty, where TC_k is the order-k total
correlation / multi-information. So building the multi-scale measure BY ANALOGY to the k=2 case -- e.g.
a nested C_rel_k = sum_S w(S) * TC(S) over higher-order feature sets S -- simply REPRODUCES the collapse
ONE ORDER UP: pairwise MI -> total correlation -> O-information. "Higher order" does NOT escape the
MI-collapse trap; it RELOCATES it to a higher-order generic statistic. (This is why constraint 4 was
strengthened to the full panel: any FIXED-order information statistic is collapsible.) The escape, if any,
is a structure CLASS that is PROVABLY NOT an analytic transform of the order-k information statistic at
ANY fixed k.

### 4.2 THE ESCAPE CANDIDATE -- a coarse-graining / renormalization FLOW object (next THEORY problem)

The candidate that is not a fixed-order joint statistic: how C TRANSFORMS under COARSE-GRAINING -- the
deferred c-merge made dynamical. The transmissible object would be the FLOW (the trajectory of C, or of
the induced weights, as the substrate is recursively coarse-grained), and its scale-INVARIANT features:
a fixed point, a critical exponent OF THE FLOW (not a static power-law fit), an anomalous dimension. The
corpus has the scaffolding but never operationalized it: Formal Foundations of Adaptive Coherence Sec 6
defines an RG-style flow g(l) = beta(l) lambda(l) with an anomalous dimension eta (per Benjamin's corpus
audit; the doc is external -- see [[cit-theory-sources]]). Constructing and validating this flow object
is the genuine NEXT THEORY PROBLEM (Benjamin + advisor) -- it is NOT this step and NOT in scope for D-cal.

### 4.3 STATUS of the multi-scale measure -- a CORPUS GAP to be CONSTRUCTED (draft correction)

Earlier framing called the recursive/multi-scale measure a "deferred higher-order" asset. That is
CORRECTED: it is a CORPUS GAP to be CONSTRUCTED, not a deferred-but-specified quantity. Specifically:
(i) the multi-scale measure is NOT yet defined anywhere in the corpus or this repo; (ii) Delta^2 C is
TEMPORAL arbitration (recursive-stability dynamics over time), NOT a measurement-layer coherence object --
the corpus is explicit that M6 / Delta^2 C "do not enter the measurement layer"; (iii) a naively NESTED-C
(C of couplings of couplings) is exactly the collapse-UP of Sec 4.1, not an escape. So the recursive
measure must be BUILT (likely as the flow object of 4.2), and that build is a prerequisite for a
non-empty cross-domain test on REAL domains.

### 4.4 The cross-domain question and the multi-scale question may be the SAME question

If the only non-collapsing transmissible representation is the flow object (4.2), the real-domain
cross-domain test is BLOCKED on first constructing it. The gating order is therefore: (1) D-cal --
validate the transfer MACHINERY on synthetic planted signal with the FLAT measure (this step, Sec 8); it
sets the concrete bar (the flat measure is BLIND to planted higher-order shared structure -- the gap the
flow object must close); (2) construct + validate the flow object (next theory problem); (3) only then a
real disjoint-prior domain pair. D-cal is step (1): a calibration, NOT a metacoherence claim.

---

## 5. CANDIDATE DISJOINT-PRIOR DOMAIN PAIRS (CC scoping -- feasibility, encoding, surrogate; do NOT pick)

Each pair lists: raw substrate, a candidate coherence computation, a buildable structured-noise
surrogate, and the MI-collapse risk (constraint 4).

### Pair 1 -- Protein MSA coupling  x  Natural-language text dependency structure
- *Substrate A:* protein multiple-sequence alignment (apparatus EXISTS in this repo); columns -> the
  coupling field.
- *Substrate B:* a text corpus -> token streams; long-range syntactic/semantic dependency or windowed
  co-occurrence structure.
- *Disjoint priors:* protein biophysics (folding/contacts) vs linguistics (syntax/semantics). No shared
  field vocabulary.
- *Surrogate:* protein -- phylogeny/position-block column permutation (preserve marginals + tree,
  destroy coupling, exactly the D2 null); text -- within-sentence shuffle preserving unigram + local
  n-gram statistics, destroying long-range dependency.
- *MI-collapse risk:* HIGH -- both reduce to pairwise symbol MI under a flat measure. This pair is the
  SHARPEST CONTROL precisely because the flat measure SHOULD collapse: it tests whether the multi-scale
  measure (Sec 4) adds anything a flat pairwise MI does not. Feasibility HIGH (both substrates trivially
  available; one substrate already in-repo).

### Pair 2 -- Music (score / MIDI)  x  Architectural floor-plan graphs
- *Substrate A:* MIDI -- a multi-voice pitch-time(-velocity) grid; coherence = harmonic / voice-leading
  recursive structure (inherently multi-scale: notes -> chords -> phrases -> form).
- *Substrate B:* a floor plan as a room-adjacency / circulation GRAPH (rooms = nodes, adjacency = edges);
  coherence = spatial-syntax recursive integration/depth (rooms -> local clusters -> building).
- *Disjoint priors:* music theory (harmony/rhythm) vs architectural space-syntax. VERY disjoint.
- *Surrogate:* MIDI -- phrase-permuted (preserve pitch histogram + local rhythm, destroy long-range
  harmonic structure); graph -- degree-preserving rewire (preserve room count + degree sequence, destroy
  circulation topology).
- *MI-collapse risk:* LOWER -- BOTH carry inherent multi-scale/recursive structure that is NOT a single
  pairwise statistic, so a scale-free recursive signature (architecture B) has something real to match.
  Best fit for INVARIANT-MATCHING + the multi-scale measure. Feasibility MEDIUM (MIDI corpora abundant
  e.g. Lakh/MAESTRO; floor-plan graph datasets exist but are smaller/less standardized; building the
  recursive measure is the real work).

### Pair 3 -- Source code (AST / token streams)  x  Genomic regulatory DNA (cis-regulatory grammar)
- *Substrate A:* source code -> token / AST-node streams; coherence = scoping / nesting / call-hierarchy
  (recursive grammar, multi-scale).
- *Substrate B:* regulatory DNA regions -> k-mer / motif streams; coherence = motif co-occurrence +
  hierarchical cis-regulatory grammar.
- *Disjoint priors:* programming-language theory vs molecular cis-regulation.
- *Surrogate:* code -- token-bigram-preserving shuffle (destroy nesting/scope, keep local token stats);
  DNA -- motif/k-mer-preserving shuffle (destroy higher-order grammar, keep composition).
- *MI-collapse risk:* MEDIUM-HIGH -- both are symbol streams whose flat measure is k-mer/co-occurrence MI;
  but both have genuine hierarchical grammar, so the multi-scale measure is where any real signal lives.
  Feasibility HIGH on substrate (huge code corpora + ENCODE/JASPAR regulatory data); MEDIUM on the
  coherence measure.

**CC observation (not a decision):** the deep open problem (Sec 4) implies pairs with INHERENT
multi-scale structure (Pair 2; or Pair 3's grammars) are stronger TEST BEDS than flat pairwise-coupling
pairs -- while Pair 1 is the strongest NEGATIVE CONTROL (it should collapse to MI, demonstrating the flat
measure transmits only the generic statistic). A staged plan could run Pair 1 as the collapse-control
FIRST, then a multi-scale invariant on Pair 2/3 -- but this is for Benjamin/advisor to rule (Sec 6).

---

## 6. OPEN QUESTIONS -- to be ruled BEFORE any build (Benjamin + advisor)

1. **ARCHITECTURE.** A (weight-transfer) / B (invariant-matching) / C (domain-translation phi)? (CC
   tentatively leans B given the MI-collapse lesson and the multi-scale fit -- but this is Benjamin's +
   advisor's call, not decided here.)
2. **DOMAIN PAIR.** One of the three scoped pairs, or another disjoint-prior pair? (Which raw substrates;
   which coherence computation; the surrogate recipe.)
3. **WHAT COUNTS AS "TRANSMIT".** A pre-specified metric + the structured-noise null it must beat
   (invariant match within a fixed tolerance where surrogates fail / a weight-prediction AUROC beating
   the surrogate null / ...). This must be FIXED before any data is fetched (the pre-reg discipline).
   **The metric MUST include a cross-domain PERSISTENCE (R1) hook (validated 2026-06-25):** transmission
   alone is an R2-type agreement claim, and a pure R2-pass with no functional/persistence content lands in
   the framework's OWN "ontologically-empty closure" cell (R1-fail / R2-pass -- structure that agrees but
   does no work). The metric must therefore require that the transmitted coherence PREDICTS persistence /
   functional structure in the TARGET domain (an R1-edge analog on B), not merely that the A and B
   coherence vectors correlate.
4. **THE MULTI-SCALE DEPENDENCY (gating; partly resolved).** Sec 4 establishes that any fixed-order
   information statistic collapses (4.1), so the escape is the flow object (4.2), which is a CORPUS GAP to
   construct (4.3). The gating order (4.4) is: (1) D-cal -- validate the transfer machinery + set the bar
   on the FLAT measure (Sec 8, pre-registered); (2) construct + validate the flow object (next theory
   problem); (3) a real disjoint-prior pair. OPEN for Benjamin/advisor: confirm this order, and whether
   the flow-object construction is taken up before any real-domain work.
5. **THE NO-MI-COLLAPSE PRE-FLIGHT GATE.** Adopt the K_comp = affine(MI) lesson as a mandatory gate:
   before any transmission claim, regress the chosen coherence measure on each domain's single generic
   statistic and confirm it is NOT an affine/monotone transform. (A measure that fails this gate cannot
   witness transmission and must be revised before the test.)

---

## 7. WHAT THIS IS NOT (discipline)

- NOT a pre-registration (no thresholds locked), NOT a build (no code), NO dataset fetched, NO lock.
- The four constraints (Sec 2) and the multi-scale dependency (Sec 4) are STANDING; the architecture,
  domain pair, transmission metric, and gating order (Sec 6) are OPEN.
- When a direction is chosen, the normal discipline applies: pre-register (thresholds fixed) -> commit +
  push the pre-reg -> run -> report -> HOLD. Reuse saved artifacts where a domain is already in-repo.
  ASCII-only in code payloads. DCA / inverse-covariance stays EXCLUDED as the Pearlian cut (P3). Nothing
  in data/ committed.

---

## 8. D-cal -- the GATING first experiment (synthetic transfer-machinery CALIBRATION)

D-cal is the cross-domain analog of D1: SYNTHETIC PLANTED-SIGNAL calibration that validates the transfer
MACHINERY and sets the concrete bar a future measure must clear. It is NOT a metacoherence claim and uses
NO real-domain data and NO flow object (that is the separate theory step of Sec 4.2).

PURPOSE -- prove the transfer machinery (i) DETECTS a planted SHARED structure across two
disjoint-vocabulary encodings, (ii) is BLIND, with the FLAT pairwise measure, to a planted PURE-HIGHER-
ORDER structure (this sets the flow object's target), and (iii) REJECTS a generic-statistics-matched null.

CONSTRUCTION (full thresholds in pre_registration.md, dated 2026-06-25 D-cal entry):
- Reuse cit/data/hsmm_d1.py for the shared latent regime trajectory T. Plant, in a derived latent feature
  array: (P) a GRADED PAIRWISE-coupled coalition (positive control -- nonzero, ranked pairwise MI), and
  (H) a PURE-HIGHER-ORDER coalition (parity triples: every pairwise MI ~ 0 by construction, but the joint
  recovers the latent regime mask -- VERIFIED near-zero, since D1's own property C is a 2-feature additive
  mask with NONZERO pairwise MI and is therefore NOT pure-higher-order, so H is built fresh).
- TWO ENCODERS render the SAME latent through stochastic emission maps with DISJOINT surface alphabets +
  independent scrambling, so NO surface n-gram statistic is shared but the latent (P and H) is identical.
- REAL-PAIR = (enc1(T), enc2(T)); NULL = (enc1(T_a), enc2(T_b)) with independent latents, per-feature
  marginals + entropy rate matched real-vs-null by construction (confirmed numerically).
- FLAT TRANSFER MEASURE (the only one tested here): per-encoder feature-pair raw-MI vector (canonical
  cit/information.py, w=ones); transfer = Spearman(enc1 vector, enc2 vector), block-bootstrap CI.

READOUTS (pre-committed): (a) P: real transfer >> null on the P-coalition pairs (machinery detects planted
pairwise structure across disjoint vocabularies); (b) H: real ~= null on the H-coalition pairs (the flat
measure is BLIND to higher-order shared structure -- sets the bar the flow object must clear); (c) null
~= 0 for both, with generic statistics equal real-vs-null. FORK: (a)+(c) hold -> machinery VALIDATED,
flow-object target set by (b); (a) fails -> the machinery is broken, fix before anything else.
