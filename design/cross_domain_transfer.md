# Cross-domain transfer -- DESIGN DRAFT (v0.7.3)

> **STATUS: DRAFT. OPEN. DECISIONS PENDING Benjamin + advisor.**
> This is a design draft to iterate on -- NOT a pre-registration, NOT a build, NO dataset fetched,
> NO code run, NO lock. Opened 2026-06-25 by the D2 (Pfam) relational FALSIFICATION (the within-domain
> protein program is exhausted as a coherence test: D2 recovered the field's pairwise-MI coevolution
> construct and nothing beyond it; K_comp = affine(raw MI) is a theorem; see pre_registration.md step-7
> and design/relational_edge_w.md Sec 7). Nothing here is committed beyond this prose. ASCII-only.

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

4. **NO MI-COLLAPSE TRAP.** Whatever coherence MEASURE is used must NOT be an analytic transform of a
   single generic statistic. This is the K_comp = affine(MI) lesson made into a pre-flight GATE: before
   any transmission claim, regress the chosen measure on each domain's single generic statistic (k-mer
   MI, co-occurrence MI, pairwise coupling) and CONFIRM it is not a monotone/affine function of it. A
   measure that collapses cannot witness transmission -- it would only transmit the generic statistic.

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
  signature (Sec 4). CC's tentative lean -- BUT Benjamin/advisor rules (Sec 6).

**(C) DOMAIN-TRANSLATION phi (the spec's M5).** Construct phi: A -> B preserving coherence up to a
monotone transform; test induced-w compatibility under phi.
- *Hard part:* HARDEST -- constructing phi without importing the priors of either domain; phi itself can
  smuggle in a shared construct and manufacture the result.
- *Feasibility:* lowest unless phi is sharply constrained (e.g. phi fixed by a non-coherence criterion,
  then coherence-compatibility tested as an out-of-sample consequence).

---

## 4. THE DEEP OPEN PROBLEM (flagged prominently)

Within each domain the FLAT FIRST-ORDER measure reduces to the field statistic (D2: -> MI; and any flat
pairwise measure on a symbol stream -> co-occurrence MI). So transmitting the flat measure would be
transmitting the generic statistic -- "statistics is universal," the empty result constraint (2) guards
against. The transmissible representation is therefore LIKELY the RECURSIVE / MULTI-SCALE coherence (the
deferred higher-order: couplings-of-couplings, motifs, cross-scale reinforcement -- design/relational_edge_w.md
Sec 8), NOT the flat pairwise measure.

**The cross-domain question and the multi-scale question may be the SAME question.** If so, the
cross-domain test is BLOCKED on first defining and validating the recursive/higher-order coherence
measure. This is the gating dependency -- it must be settled before (or as) any cross-domain build:
either (a) the multi-scale measure is defined first and the cross-domain test is its first real
application, or (b) a cross-domain test on the flat measure is run ONLY as a NEGATIVE control to confirm
the flat measure DOES collapse (transmits only the generic statistic), motivating the multi-scale step.

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
4. **THE MULTI-SCALE DEPENDENCY (gating).** Is the cross-domain test BLOCKED on first defining the
   recursive/higher-order coherence measure (Sec 4)? If the flat measure collapses to the field
   statistic in EACH domain, transmitting it is empty -- so do we (a) define the multi-scale measure
   first and make cross-domain its first application, or (b) run a flat-measure cross-domain test ONLY as
   a negative collapse-control? This may be the FIRST thing to settle.
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
