# Pre-registration: Can open LLMs clear sanctions-screening alerts?

Date: 2026-11-04. Written before any LLM call on the study data (only the deterministic stage-1 screening
of the pilot set had been computed). Author: Mehmet Murat Huyut. Any change after sealing is logged at the
bottom with a date and reason.

## Research question
Sanctions screening in banks raises name-based alerts, most of which are innocent customers who share or
resemble a listed person's name. Can open-weight LLMs that a bank can run on premises or on domestic
infrastructure clear these alerts at level 1, without missing listed persons, with an auditable reason,
and at what cost, compared with rule-based disposition?

## Data (public or synthetic only; no bank or customer data)
- Watch list: UK Sanctions List (FCDO, Open Government Licence v3.0) and the EU consolidated financial
  sanctions list (FSF, Commission Decision 2011/833/EU), both downloaded 2026-11-04 (SHA-256 in
  `data/raw/SHA256SUMS`). Scope: natural persons with at least one recorded date of birth and at least
  one Latin-script name (7,103 entries; entries of the same person on both lists are linked when they
  share a normalised name and a date of birth). The OFAC SDN list was planned but could not be
  downloaded from this machine on the registration date; it is not used.
- Synthetic customers (`deney/musteri.py`, seed 20261104). Pilot and full sets are drawn from disjoint
  persons (12% of persons reserved for the pilot).
  - Positive customers (the listed person): 6 name conditions x 2 date-of-birth conditions.
    Name: exact primary name; a good-quality alias; Turkish spelling of an Arabic-origin name
    (e.g. Muhammad Abd al-Rahman -> Muhammed Abdurrahman); Turkish romanisation of a Cyrillic name;
    word order / dropped middle name or patronymic; one or two typing errors with Turkish upper case.
    Date of birth: compatible with the list; or a minor discrepancy as defined in the policy
    (day-month transposition, year +/-1 with the same day and month, one digit).
  - Negative customers: (a) namesakes - the same six name conditions with a date of birth at least five
    years from every listed date of the person; (b) near-name - the family name replaced with a different,
    similar-looking family name (at least 3 edits, consonant skeleton differs by at least 2), same date of
    birth; (c) general population - common Turkish names (70%) and recombined given and family names from
    the list (30%) with random dates of birth.
  - Sizes: full set 100 per positive cell (1,200), 100 per namesake condition (600), 400 near-name,
    10,000 general; pilot 10 / 10 / 40 / 2,000.
- Bank policy for level-1 disposition: `deney/politika.md` (identical text in the LLM prompt and in the
  rule baseline).

## Pipeline
- Stage 1 (screening, deterministic): channel F = fuzzy name matching (rapidfuzz token_set_ratio on
  normalised Latin names; entry score = best name); an alert is raised for every entry with F >= 85, at most
  the top 5 per customer. Channel E = multilingual embedding similarity (bge-m3, run locally) over all names
  including non-Latin; E adds entries ranked in the top 3 by cosine with cosine >= tau that are not already
  F alerts. tau is fixed on the pilot set by this rule: the smallest value on a 0.01 grid at which general-
  population pilot customers receive on average at most 0.10 E-only alerts each. Pipelines: F and F+E.
- Stage 2 (level-1 disposition of each alert):
  - R0: no disposition (every alert goes to level 2).
  - R1 strict rule: escalate iff the date of birth matches exactly (on the components the list gives).
  - R2 policy rule: discount iff the policy's date-of-birth conflict condition holds; otherwise escalate
    if F >= 85, else discount (the name condition is represented by the fuzzy score).
  - LLMs, each given the policy, the customer record and the full list entry, returning JSON with
    name_assessment, dob_assessment, decision and reason. Temperature 0, fixed seed, thinking disabled.
    Domestic API (EVREN): deepseek-v4.1-flash, qwen3.8-flash-next, gemma-4-31b, glm-5.3.
    Local (Ollama on the author's machine): qwen3.8:27b-mxfp8, gemma4:31b, gpt-oss:20b.
- A customer is escalated if any of its alerts is escalated.

## Ground truth and exclusions
- Positive customer: correct disposition is escalate, provided stage 1 raised an alert on the person's own
  entry (or a linked entry); otherwise the miss is attributed to stage 1.
- Negative customer: correct disposition is discount of every alert, provided every alert meets a policy
  discount condition by construction (a date-of-birth conflict, or for near-name customers on the source
  entry, the different family name). Negative customers with any alert that meets neither condition are
  "indeterminate" and excluded; their number is reported.

## Outcomes
- Primary: (1) miss rate - share of positive customers with a stage-1 alert on their own entry that are not
  escalated; (2) level-2 workload - escalated negative customers per 1,000 screened customers, and the
  false-positive rate among alerted negative customers.
- Secondary: stage-1 recall by cell and channel; rationale accuracy (the stated dob_assessment against the
  deterministic status; the stated name_assessment against the construction); decision-rationale
  consistency (the decision follows the model's own assessments under the policy); parse failures;
  tokens, latency and EVREN credit per alert and per 1,000 customers.

## Hypotheses (confirmatory, full set)
- H1 (safety): for each LLM, the miss rate in pipeline F is not more than 2 percentage points above R2's
  (non-inferiority; upper bound of the 95% paired Newcombe interval of the difference < 2 pp).
- H2 (workload): for each LLM, fewer alerted negative customers are escalated than under R2 in pipeline F
  (exact McNemar, one-sided).
- H3 (transliteration and stage 1): F-channel recall is lower for the two Turkish-transliteration name
  conditions than for the exact-name condition, and adding channel E raises recall in those conditions
  (exact McNemar).
- H4 (LLM with a wider net): in pipeline F+E, each LLM escalates more positive customers than R2
  (exact McNemar, one-sided), because R2 discounts E-only alerts below the fuzzy threshold.
- H5 (date discrepancies): LLM miss rates are higher under the minor date-of-birth discrepancy condition
  than under the compatible condition (Fisher's exact test, one-sided).
- H6 (rationale accuracy): for each LLM, the stated dob_assessment agrees with the deterministic status
  in at least 95% of alerts (one-sided exact binomial test against 0.95; supported if the lower 95% bound
  exceeds 0.95).
- H7 (deployment): the same open model served on domestic infrastructure (EVREN gemma-4-31b) and locally
  (Ollama gemma4:31b) gives the same decision on at least 95% of alerts (upper 95% bound of the
  disagreement rate below 5%).

## Analysis plan
- Wilson 95% intervals for all rates; exact McNemar tests on paired customers; Holm correction across the
  LLMs within each of H1, H2, H4, H5 and H6. Cell-level tables are descriptive.
- Parse failures and missing responses after retries count as escalate (the safe default of a level-1
  queue) and are reported separately; a sensitivity analysis treats them as discount.
- Cost: input and output tokens, median latency, and EVREN credit change measured from the
  X-Evren-Credits-Remaining response header.

## Gates (pilot)
- The pilot set is used only to check the pipeline and to fix tau; it is excluded from the confirmatory
  analysis.
- Proceed to the full run only if, for every model, at least 90% of alerts return a parseable decision,
  and F-channel recall on exact-name positives is at least 95%.
- A model whose pilot latency implies a full run longer than 72 hours may be dropped from the full run;
  the decision is logged here before the full run.
- The full run on EVREN starts only after the author has seen the measured credit cost of the pilot and
  approved it.

## Decisions taken before sealing (pilot stage-1 output only; no LLM output on study data seen)
- Stage-1 scorer: WRatio >= 85 raised alerts for 53% of general-population pilot customers (2.3 alerts
  per customer). On the same pilot screening output, token_set_ratio >= 85 gave 8% with full recall on
  exact, alias and word-order positives, and was adopted. The full general population was reduced from
  20,000 to 10,000 to bound LLM cost.
- Near-name ground truth: the family-name condition is checked against every alerted entry with the same
  criterion used to generate the name (the second, unlinked entry of the same person on the other list
  would otherwise be indeterminate).
- A smoke test on one fictional alert (not study data) returned parseable JSON from all seven models.
  Median latency of glm-5.3 was 385 s per call, so glm-5.3 is piloted on a random subsample of 150 alerts
  (seed 7); the full-run decision for glm-5.3 follows the 72-hour gate.
- tau (channel E) = 0.79 by the registered rule (`data/e_tau.json`).

## Changes after pre-registration

### Amendment 1 (2026-11-04, during the pilot; before any pilot analysis)
**Decision (author).** All remaining pilot runs and the full run use only the domestic API (EVREN). Of the
local Ollama models, only qwen3.8:27b-mxfp8 completes the pilot; gemma4:31b and gpt-oss:20b are not run
(their partial pilot output is moved to `data/runs/pilot_iptal/` and not analysed). H7 (same model on
domestic infrastructure versus local serving) is withdrawn.
**Reason.** The study's claim about on-premises use rests on the models being open-weight: any bank with
the GPU capacity can deploy them, so the claim does not require running them locally here. Local runs also
compete for the author's workstation. The qwen3.8:27b-mxfp8 pilot result may be reported as exploratory.
**Not a protocol change.** Concurrency for EVREN requests is raised from 4 to 12 parallel requests per
model to keep the run within a working day; it does not change prompts, parameters or scoring.

### Amendment 2 (2026-11-04, after the pilot gate; before the full run)
**Gate result.** F-channel recall on exact-name pilot positives was 100%. Parse rates: gemma-4-31b 100%,
qwen3.8-flash-next 100%, deepseek-v4.1-flash 96.2%, glm-5.3 59.3% (150-alert subsample). Every unparsed
glm-5.3 reply used the full 1,500-token output budget and returned empty content (hidden reasoning), so
glm-5.3 fails the 90% parse gate.
**Decision (author).** glm-5.3 is dropped from the full run on the gate; its prompt and parameters are not
changed. The full run uses deepseek-v4.1-flash, qwen3.8-flash-next and gemma-4-31b on EVREN; both EVREN
accounts may be used. The glm-5.3 pilot result is reported as a gate failure. Hypotheses H1-H6 are tested
for these three models; Holm corrections run over three models.
**Cost measurement.** The X-Evren-Credits-Remaining header stayed at 1000.0000 over all 3,016 pilot calls
(2.35 M tokens), so cost is reported as tokens and latency; the credit field is still logged.

## Deviations found after the full-run analysis (not amendments; reported in the paper)

### Deviation 1 (2026-11-05): minor date-of-birth discrepancy generator
**Found.** After the confirmatory tests, R2's misses in pipeline F were traced: all 20 are D_kucuk positives
whose constructed date of birth is a policy conflict with the person's own entry. In `dob_kucuk`
(`deney/musteri.py`), the one-digit change of the day falls back to day 18 when the changed day is 0 or
above 28, which for list days 28-31 is not a minor discrepancy. 21 of 600 D_kucuk positives in the full set
are affected (20 with an F alert on their own entry); 2 of 60 in the pilot (not noticed at the gate).
**Handling.** The data are not regenerated and nothing is rerun. The registered analysis is reported as
registered. A post hoc sensitivity analysis that excludes the affected customers is reported next to it for
H1, H4 and H5 (`scripts/hipotez.py`, `data/hipotez_full.json`). Without them R2 misses no positive in
pipeline F, H1 is not supported for any LLM and H4 is not supported; H2, H3 and H6 do not depend on these
customers.
