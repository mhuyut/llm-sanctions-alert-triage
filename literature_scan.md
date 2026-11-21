# Literature scan: LLMs in banking KYC / CDD (arXiv, cs.CL)

Scan date: 2026-11-04. Prepared for the arXiv paper by Dr. Mehmet Murat Huyut.
Research question: *Can LLMs be used in banking KYC (customer due diligence) processes?* The study uses open models hosted locally or in-country (DeepSeek-V4-Flash, Qwen3.8, Gemma-4-31B, GLM-5.3, Qwen3-VL, dots.ocr). It runs a preregistered experiment on large public data and compares the models against rule-based and classical baselines.

## How the sources were checked

- **arXiv:** every arXiv item was read live through the arXiv API (`export.arxiv.org/api/query`, `search_query` and `id_list`). The abstract, author list, primary category, comment and journal_ref fields were all read.
- **DOIs:** checked with the Crossref REST API (`api.crossref.org/works/{doi}` and `works?query.bibliographic=`). No `mailto` parameter and no e-mail address was sent to any service.
- **EU law:** read from the EU Publications Office (`publications.europa.eu/resource/celex/<CELEX>`, XHTML).
- **Turkish law:**
  - Laws 5549, 6415, 7262 and 6698 come from mevzuat.gov.tr (`/MevzuatMetin/1.5.<no>.pdf`, with curl).
  - The MASAK and BDDK regulations come from the official Resmî Gazete archive (resmigazete.gov.tr/eskiler/...), with curl. This is the **original published text**. The consolidated (amended) text on mevzuat.gov.tr could not be located by URL, so it was **not checked**.
- **FATF:** fatf-gafi.org returns HTTP 403 or a Cloudflare challenge to both curl and WebFetch. The official FATF pages and PDFs were therefore read through **Wayback Machine snapshots of the official URLs** (snapshot timestamps are given below). This is an archived copy of the official source, not the live site.
- **Status labels:**
  - **VERIFIED:** I saw the record live, including the abstract or the legal text.
  - **VERIFIED (metadata):** I saw the bibliographic record live, but no abstract was available. Crossref had none, and Springer, IEEE Xplore and ACM blocked command-line access. The summary for these items is restricted to what the title and record establish.
- **Not done:** no item was taken from memory without a live check. Nothing has been checked against a claim in the manuscript yet, because the manuscript does not exist.

---

## 1. LLMs for KYC / CDD / EDD, onboarding, adverse media, risk rating

| Key | Reference | Status | What it actually shows |
|---|---|---|---|
| `chernakov2025adverse` | Chernakov, P., Jafarnejad, S., Frank, R. (2025). *An Agentic LLM Framework for Adverse Media Screening in AML Compliance.* arXiv:2602.23373 [cs.AI] (v1 dated 2025-12-29). | VERIFIED | An LLM agent with RAG searches the web, retrieves documents and computes an "Adverse Media Index" per subject. It was evaluated with several LLM backends on PEPs, watch-listed and sanctioned persons from OpenSanctions, plus clean names. The goal is to replace keyword search, which produces many false positives. |
| `khandpur2020adverse` | Khandpur, R. P., Nanda, A. A., Davis, M., Li, C., Nurmanbetov, D., Gaur, S., Talukder, A. (2020/2021). *Adverse Media Mining for KYC and ESG Compliance.* KDD 2020 Workshop on ML in Finance; arXiv:2110.11542 [cs.IR]. | VERIFIED | A pre-LLM baseline: a deployed ML system for real-time and batch adverse-news filtering. It scores relevance to risk domains, entity relevance, adverse sentiment and risk encoding. |
| `wahib2026spectra` | Wahib, M., Tran, E., Mourad, R., Muti, M., Dvornik, N. (2026). *Spectra: A Rules-Driven LLM Pipeline for Automated KYC Document Processing.* arXiv:2609.25474 [cs.AI]. | VERIFIED | KYC onboarding in capital markets. A rules engine encodes policy, and LLM agents classify, extract and validate documents. On real (non-public) KYC documents: 100% classification accuracy, 89.4% extraction accuracy, and 96% less human review. **Close to our study, but uses proprietary data and has no public benchmark or classical baseline.** |
| `he2025aria` | He, Y., Li, R., Chen, A., Liu, Y., Chen, Y., Sui, Y., Chen, C., Zhu, Y., Luo, L., Yang, F., Hooi, B. (2025). *Enabling Self-Improving Agents to Learn at Test Time With Human-In-The-Loop Guidance.* EMNLP 2025 Industry Track, pp. 1625–1653. doi:10.18653/v1/2025.emnlp-industry.115; arXiv:2507.17131. | VERIFIED | The ARIA agent learns updated rules at test time from expert feedback. It was evaluated on **CDD name screening at TikTok Pay** (production, proprietary data) and outperformed fine-tuning and self-improving-agent baselines. |
| `naik2025coinvestigator` | Naik, P. V., Dintakurthi, N. K., Hu, Z., Wang, Y., Qiu, R. (2025). *Co-Investigator AI: The Rise of Agentic AI for Smarter, Trustworthy AML Compliance Narratives.* arXiv:2509.08380 [cs.AI]. | VERIFIED | A multi-agent framework for drafting SAR narratives: planning, typology detection, external intelligence, a privacy-guard layer, and an agent-as-judge validator, with a human in the loop. Shown on financial-crime scenarios; the abstract reports no public benchmark numbers. |
| `torres2026triage` | Torres, D., Cheng, W., Hu, K. (2026). *Explainable AML Triage with LLMs: Evidence Retrieval and Counterfactual Checks.* arXiv:2604.19755 [cs.AI]. | VERIFIED | Alert triage under an evidence-constrained output contract (citations, supporting vs. contradicting evidence) with counterfactual checks. Run on **public synthetic AML benchmarks against rule, tabular and graph-ML baselines**. Results: PR-AUC 0.75, escalate-F1 0.62, citation validity 0.98, counterfactual faithfulness 0.76. **Methodologically closest on the AML side.** |
| `naik2026llmops` | Naik, P. V., Dintakurthi, N., Wang, Y. (2026). *Rethinking LLMOps for Fraud and AML: Building a Compliance-Grade LLM Serving Stack.* arXiv:2605.11232 [cs.AI]. | VERIFIED | A serving stack (vLLM, prefix caching, multi-adapter) for **self-hosted open-weight models (Llama, Qwen)** on AML prompts. It turns IBM AML and SAML-D into compliance prompts and adds an LLM-as-judge quality gate. It is about systems and cost, not detection accuracy. Useful for the cost and on-premise argument. |
| `pirmorad2025icl` | Pirmorad, E. (2025). *Exploring the In-Context Learning Capabilities of LLMs for Money Laundering Detection in Financial Graphs.* 2025 IEEE ICDM Workshops (ICDMW), pp. 174–177. doi:10.1109/ICDMW69685.2025.00026; arXiv:2507.14785. | VERIFIED | k-hop subgraphs are serialised to text, and few-shot LLMs judge suspiciousness and write justifications on synthetic AML scenarios. The author calls it exploratory: there is no quantitative baseline comparison in the abstract. |
| `koletsis2024corruption` | Koletsis, P., Gemos, P.-K., Chronis, C., Varlamis, I., Efthymiou, V., Papadopoulos, G. Th. (2024). *Entity Extraction from High-Level Corruption Schemes via Large Language Models.* arXiv:2409.13704 [cs.CL]. | VERIFIED | A micro-benchmark for extracting persons and organisations (and their name variants) from financial-crime news with low-billion-parameter LLMs. Includes LLM-based disambiguation and beats an open-source NER baseline. Relevant to adverse-media entity extraction. |
| `pavlidis2023ai` | Pavlidis, G. (2023). *Deploying artificial intelligence for anti-money laundering and asset recovery: the dawn of a new era.* Journal of Money Laundering Control, 26(7), 155–166. doi:10.1108/JMLC-03-2023-0050. | VERIFIED | A legal and policy analysis of AI in AML/CFT against the FATF San José principles, the OECD AI principles and the (then proposed) EU AI Act. It argues for safeguards that balance efficiency with fundamental rights. |
| `reite2024client` | Reite, E. J., Karlsen, J., Westgaard, E. G. (2024). *Improving client risk classification with machine learning to increase anti-money laundering detection efficiency.* Journal of Money Laundering Control, 28(1), 93–107. doi:10.1108/JMLC-03-2024-0040. | VERIFIED | Uses real bank SME data. ML client-risk classification predicts future suspicious transactions, and accounting and credit data improve it. Motivated by false-positive workload. A classical **customer risk-rating** baseline reference. |
| `han2020aml` | Han, J., Huang, Y., Liu, S., Towey, K. (2020). *Artificial intelligence for anti-money laundering: a review and extension.* Digital Finance, 2(3–4), 211–239. doi:10.1007/s42521-020-00023-1. | VERIFIED (metadata) | A review of AI for AML (abstract not accessible: Springer blocked). Cite only as a general review. |
| `chen2018mlaml` | Chen, Z., Van Khoa, L. D., Teoh, E. N., Nazir, A., Karuppiah, E. K., Lam, K. S. (2018). *Machine learning techniques for anti-money laundering (AML) solutions in suspicious transaction detection: a review.* Knowledge and Information Systems, 57(2), 245–285. doi:10.1007/s10115-017-1144-z. | VERIFIED (metadata) | A review of ML techniques for suspicious-transaction detection (abstract not accessible). Cite only as a review. |

**Searched but not found:** an LLM study of **beneficial-ownership extraction** from public registries (the arXiv query `all:"beneficial ownership"` returned only one design-science identity paper), and an LLM **CDD/EDD risk rating with explanations** evaluated on public data. Both appear to be open gaps.

## 2. Name matching and sanctions screening

| Key | Reference | Status | What it actually shows |
|---|---|---|---|
| `smith2026opensanctions` | Smith, C., Sesodia, M., Lindenberg, F., Schroeder de Witt, C. (2026). *OpenSanctions Pairs: Large-Scale Entity Matching with LLMs.* arXiv:2603.11051 [cs.IR] (v2, 2026-02-24). | VERIFIED | **The closest prior work.** It releases 755,540 expert-labelled pairs over more than 1M entities from 293 sources in 45 jurisdictions, in Latin, Cyrillic and Arabic script. Results: rule-based nomenklatura RegressionV1 reaches 91.3% F1, GPT-4o 99.0% F1, and the **locally deployable** DeepSeek-R1-Distill-Qwen-14B 98.2% F1, with and without MIPROv2 prompt optimisation. Rules over-match, while LLMs fail on cross-script transliteration. The authors argue pairwise matching is near a ceiling and that attention should shift to blocking, clustering and review. |
| `chourasia2026sger` | Chourasia, S., Kapoor, H., Patil, N. (2026). *Structure-Guided Entity Resolution: Fine-Tuning LLMs for Robust Name Matching in Complex Linguistic Contexts.* Proc. ACL 2026 (Vol. 6: Industry Track), pp. 1461–1468. doi:10.18653/v1/2026.acl-industry.101; arXiv:2605.23597. | VERIFIED | A curriculum fine-tuned LLM (name-structure parsing first, then matching) on Indian KYC identity data. Accuracy 99.02%, F1 0.994 on 50k real pairs, better than GPT-4o few-shot. Deployed at Dream11. The data is proprietary. |
| `gopal2026crossscript` | Gopal, A., Pravin, P. P., Kadu, A., Jain, A., Krishnan, A. (2026). *Same Entity, Different Script: Diagnosing Cross-Script Entity Matching Failures in Language Models.* arXiv:2610.31407 [cs.CL]. | VERIFIED | On 601 audited Devanagari/Latin pairs, Qwen2.5-7B same-person accuracy falls from 35.1% (Latin) to 8.5% (Devanagari), and to 5.3% for Malayalam, while AUROC stays high (0.925). The main cause is decision-criterion placement: calibration recovers much of the gap. **Direct evidence for a cross-script hypothesis and for calibrating thresholds.** |
| `gupta2026corpfam` | Gupta, H. (2026). *Corporate-Family Resolution Is Not a String-Matching Problem: A Public Benchmark Stratified by Name Visibility.* arXiv:2609.04269 [cs.DB]. | VERIFIED | The CorpFam benchmark has 54,864 pairs from US federal award records. Matchers recover 100% of identical-name pairs but at most 4.7% of "invisible" ones, and blocking is the bottleneck. Relevant to sanctions screening of related entities and to reporting per-stratum recall. |
| `zeakis2026distiller` | Zeakis, A., Papadakis, G., Skoutas, D., Koubarakis, M. (2026). *DistillER: Knowledge Distillation in Entity Resolution with Large Language Models.* arXiv:2602.05452 [cs.DB]. | VERIFIED | Distils large LLM teachers into small students for entity resolution without gold labels, to cut cost. Relevant to the cost/efficiency trade-off for local models. |
| `li2024booster` | Li, H., Li, S., Hao, F., Zhang, C. J., Song, Y., Chen, L. (2024). *BoostER: Leveraging Large Language Models for Enhancing Entity Resolution.* WWW '24 Companion (demo). doi:10.1145/3589335.3651245; arXiv:2403.06434. | VERIFIED | A demo that selects matching questions to send to an LLM and refines the ER result distribution. Argues for low cost and easy deployment. |
| `fellegi1969theory` | Fellegi, I. P., Sunter, A. B. (1969). *A Theory for Record Linkage.* Journal of the American Statistical Association, 64(328), 1183–1210. doi:10.1080/01621459.1969.10501049. | VERIFIED (metadata) | The probabilistic record-linkage foundation, used as the classical baseline reference. |
| `jaro1989advances` | Jaro, M. A. (1989). *Advances in Record-Linkage Methodology as Applied to Matching the 1985 Census of Tampa, Florida.* JASA, 84(406), 414–420. doi:10.1080/01621459.1989.10478785. | VERIFIED (metadata) | The source of the Jaro string comparator (the basis of Jaro–Winkler). |
| `christen2012datamatching` | Christen, P. (2012). *Data Matching: Concepts and Techniques for Record Linkage, Entity Resolution, and Duplicate Detection.* Springer. doi:10.1007/978-3-642-31164-2. | VERIFIED (metadata; title from Crossref shows "Data Matching") | A standard textbook on blocking, field comparison (incl. Jaro–Winkler) and classification. The full subtitle was not visible in Crossref; check it before citing. |
| `bilenko2003adaptive` | Bilenko, M., Mooney, R., Cohen, W., Ravikumar, P., Fienberg, S. (2003). *Adaptive name matching in information integration.* IEEE Intelligent Systems, 18(5), 16–23. doi:10.1109/MIS.2003.1234765. | VERIFIED (metadata) | A classic comparison of static and learned string-similarity measures for name matching. |
| `pouliquen2005multilingual` | Pouliquen, B., Steinberger, R., Ignat, C., Temnikova, I., Widiger, A. (2005). *Multilingual person name recognition and transliteration.* Corela, HS-2. doi:10.4000/corela.1219. | VERIFIED (metadata) | JRC work on recognising and transliterating person names across languages and scripts. Background for Cyrillic and Arabic variants. |
| `ofac_sdn` | U.S. Treasury OFAC. *Specially Designated Nationals and Blocked Persons List (SDN) Human Readable Lists.* https://ofac.treasury.gov/specially-designated-nationals-and-blocked-persons-list-sdn-human-readable-lists (accessed 2026-11-04, HTTP 200). | VERIFIED | Official list page (data source). |
| `eu_fsf_list` | European Union. *Consolidated list of persons, groups and entities subject to EU financial sanctions.* data.europa.eu dataset page (accessed 2026-11-04, HTTP 200). | VERIFIED | Official EU open-data entry (data source). |
| `un_sc_list` | United Nations Security Council. *United Nations Security Council Consolidated List.* https://main.un.org/securitycouncil/en/content/un-sc-consolidated-list (accessed 2026-11-04). | VERIFIED | Official UN list page (data source). |
| `opensanctions_default` | OpenSanctions. *OpenSanctions Default dataset.* https://www.opensanctions.org/datasets/default/ (accessed 2026-11-04). | VERIFIED | Aggregated sanctions, PEP and watchlist data (data source). Check the licence: non-commercial terms may apply (not verified here). |

**Searched but not found:**
- No arXiv or Crossref paper on **Turkish name matching or transliteration** for KYC or sanctions. Queries: `Turkish AND "name matching"`, `Turkish AND "record linkage"`, and a Crossref "Turkish personal names record linkage". Turkish characters (ç, ğ, ı/İ, ö, ş, ü), their ASCII-folding and Arabic-origin names transliterated into Latin and Cyrillic look like an **open gap**.
- No peer-reviewed study quantifying the **false-positive burden of sanctions screening**. Crossref returned only SSRN preprints (not cited). The alert-level false-positive evidence comes from transaction monitoring (Section 4: Naser Eddin et al., Reite et al.).

## 3. Identity documents: datasets, VLM/OCR extraction, forgery detection

| Key | Reference | Status | What it actually shows |
|---|---|---|---|
| `arlazarov2019midv500` | Arlazarov, V. V., Bulatov, K., Chernov, T., Arlazarov, V. L. (2019). *MIDV-500: A dataset for identity documents analysis and recognition on mobile devices in video stream.* Computer Optics, 43(5), 818–824. doi:10.18287/2412-6179-2019-43-5-818-824; arXiv:1807.05786. | VERIFIED | 500 video clips of 50 identity document types with ground truth. Source images are public domain or openly licensed. Gives baselines for face detection, text-line recognition and field extraction. |
| `bulatov2020midv2019` | Bulatov, K., Matalov, D., Arlazarov, V. V. (2020). *MIDV-2019: Challenges of the modern mobile-based document OCR.* Proc. SPIE 11433, ICMV 2019, 114332N. doi:10.1117/12.2558438; arXiv:1910.04009. | VERIFIED | Extends MIDV-500 with strong projective distortion and low light, plus text-field recognition baselines. |
| `bulatov2022midv2020` | Bulatov, K., Emelianova, E., Tropin, D., Skoryukina, N., Chernyshova, Y., Sheshkus, A., Usilin, S., Ming, Z., Burie, J.-C., Luqman, M. M., Arlazarov, V. V. (2022). *MIDV-2020: A Comprehensive Benchmark Dataset for Identity Document Analysis.* Computer Optics, 46(2), 252–270. doi:10.18287/2412-6179-CO-1006; arXiv:2107.00396. | VERIFIED | 1,000 unique mock IDs with synthetic faces: 1,000 videos, 2,000 scans, 1,000 photos, 72,409 annotated images. Baselines for location, type identification, field recognition and face detection. **The most suitable public set for VLM field extraction.** |
| `guan2024idnet` | Guan, H., Wang, Y., Xie, L., Nag, S., Goel, R., Swamy, N. E. N., Yang, Y., Xiao, C., Prisby, J., Maciejewski, R., Zou, J. (2024). *IDNet: A Novel Dataset for Identity Document Analysis and Fraud Detection.* arXiv:2408.01690 [cs.CV]. | VERIFIED | 837,060 synthetic ID images (~490 GB) of 20 types from 10 US states and 10 European countries, with fraud patterns. Argues that MIDV-500, MIDV-2020 and FMIDV are too small for fraud work. |
| `korshunov2025fantasyid` | Korshunov, P., Mohammadi, A., Vidit, V., Ecabert, C., Marcel, S. (2025). *FantasyID: A Dataset for Detecting Digital Manipulations in ID-Documents.* 2025 IEEE IJCB, pp. 1–9. doi:10.1109/IJCB65343.2025.11411292; arXiv:2507.20808. | VERIFIED | Printed and recaptured fantasy IDs with real faces, plus digital forgery and injection attacks. At an operational threshold of 10% FPR, state-of-the-art detectors (TruFor, MMFusion, UniFD, FatFormer) show FNR near 50%. |
| `zhao2026docforge` | Zhao, Z., Xia, W., Wei, E., Zhang, Y., Mo, J., Zhang, T., Dai, Y., Chen, Z., Tao, Y., Ren, S. (2026). *DOCFORGE-BENCH: A Comprehensive 0-shot Benchmark for Document Forgery Detection and Analysis.* arXiv:2603.01433 [cs.CV]. | VERIFIED | 14 methods on 8 datasets, including ID manipulation, zero-shot. Pixel-AUC is moderate but Pixel-F1 is near zero: a calibration and threshold failure. Adapting the threshold on 10 domain images recovers 39–55% of the oracle-F1 gap. |
| `kumar2026flid` | Kumar, A., Tapwal, R., Maple, C., Hooper, M. (2026). *Field-Localized Forgery Detection for Digital Identity Documents.* arXiv:2605.09089 [cs.CV]. | VERIFIED | A lightweight detector that works on face and text fields (YOLO11 + MobileNetV3). AUC 0.834 / 0.926 / 0.837 for face, text and combined attacks; EER 28–29 points lower than a full-document baseline. Framed for eKYC. |
| `das2026idsurvey` | Das, G., Kumar C, P., Ramachandra, R. (2026). *From Forgeries to Foundation Models: A Systematic Survey of Identity Document Attack and Detection.* arXiv:2607.01442 [cs.CR]. | VERIFIED | A survey of presentation, injection and GenAI attacks. It reports a "reality gap" in 2019–2025 datasets and script-dependent generative instability in non-Latin inpainting. Zero-shot APCER is above 25%. |
| `vinogradov2025forge` | Vinogradov, A. (2025). *Can Generative Models Actually Forge Realistic Identity Documents?* arXiv:2601.00829 [cs.CV]. | VERIFIED | Open diffusion models reproduce the surface look of documents but not their structural or forensic authenticity. Argues that the risk of GenAI ID forgery may be overestimated. |
| `xu2026docprivacy` | Xu, B., Wang, H., Wang, J., Chen, C., Chakraborty, A. (2026). *Beyond Visual Evidence: Revealing and Mitigating Relational Privacy Leakage in Document MLLMs.* ACM MM 2026; arXiv:2608.12911. DOI listed on arXiv: 10.1145/3767308.3835901 (**not yet resolvable in Crossref**, 404 on 2026-11-04). | VERIFIED (arXiv) | Document MLLMs doing key-information extraction on IDs **fill in missing fields from memorised field relations**, which leaks personal data. Introduces DocPrivacyBench and an unlearning method. Relevant to hallucination risk in VLM extraction. |
| `amada2025ekyc` | Amada, T., Kakizaki, K., Miyagawa, T., Ebihara, A. F., Shiohara, K., Yamasaki, T. (2025). *Robust Deepfake Detection for Electronic Know Your Customer Systems Using Registered Images.* IEEE FG 2025 (per arXiv comment); arXiv:2507.22601 [cs.CV]. | VERIFIED | A deepfake (face-swap and reenactment) detector for eKYC video that compares against a registered genuine image. |
| `bai2025qwen3vl` | Bai, S., Cai, Y., Chen, R., et al. (64 authors) (2025). *Qwen3-VL Technical Report.* arXiv:2511.21631 [cs.CV]. | VERIFIED | Model card for the Qwen3-VL family: dense 2B–32B and MoE 30B-A3B / 235B-A22B, native 256K context. |
| `li2025dotsocr` | Li, Y., Yang, G., Liu, H., Wang, B., Zhang, C. (2025). *dots.ocr: Multilingual Document Layout Parsing in a Single Vision-Language Model.* arXiv:2512.02498 [cs.CV]. | VERIFIED | A single VLM for layout detection, text recognition and relations. State of the art on OmniDocBench; introduces XDocParse (126 languages). |
| `liu2024ocrbench` | Liu, Y., Li, Z., Huang, M., Yang, B., Yu, W., Li, C., Yin, X.-C., Liu, C.-L., Jin, L., Bai, X. (2024). *OCRBench: on the hidden mystery of OCR in large multimodal models.* Science China Information Sciences, 67(12). doi:10.1007/s11432-024-4235-6; arXiv:2305.07895. | VERIFIED | A text-centric evaluation of large multimodal models (GPT-4V, Gemini, ...) on OCR tasks. |

**Searched but not found:** a study evaluating **open VLMs (Qwen-VL / dots.ocr class) for field extraction on MIDV-2020** against classical OCR. Queries: `"MIDV-2020"`, `"identity documents" AND "multimodal large language"`, `passport AND "vision-language"`. Only the privacy-leakage paper above uses document MLLMs on IDs. This looks like a gap.

## 4. AML transaction monitoring: datasets, baselines, LLM triage and SAR

| Key | Reference | Status | What it actually shows |
|---|---|---|---|
| `altman2023amlworld` | Altman, E., Blanuša, J., von Niederhäusern, L., Egressy, B., Anghel, A., Atasu, K. (2023). *Realistic Synthetic Financial Transactions for Anti-Money Laundering Models.* Advances in Neural Information Processing Systems 36 (NeurIPS 2023, Datasets & Benchmarks), pp. 29851–29874. doi:10.52202/075280-1300; arXiv:2306.16424. | VERIFIED (Crossref and proceedings.neurips.cc page, HTTP 200) | IBM AMLworld: an agent-based generator calibrated to real transactions, released as public datasets. Ground-truth labels are complete, unlike real data where much laundering goes undetected. Used to compare ML models. |
| `oztas2023samld` | Oztas, B., Cetinkaya, D., Adedoyin, F., Budka, M., Dogan, H., Aksu, G. (2023). *Enhancing Anti-Money Laundering: Development of a Synthetic Transaction Monitoring Dataset.* 2023 IEEE ICEBE, pp. 47–54. doi:10.1109/ICEBE59045.2023.00028. | VERIFIED (metadata; IEEE Xplore page did not render) | The SAML-D synthetic transaction-monitoring dataset. Dataset size and typology counts were **not verified** here and must be read from the paper or dataset card before citing. |
| `lopezrojas2018paysim` | Lopez-Rojas, E. A., Axelsson, S., Baca, D. (2018). *Analysis of fraud controls using the PaySim financial simulator.* International Journal of Simulation and Process Modelling, 13(4), 377. doi:10.1504/IJSPM.2018.093756. | VERIFIED (metadata) | PaySim mobile-money simulator applied to fraud controls. The original 2016 EMSS PaySim paper was **not found** in Crossref; cite this journal version. |
| `weber2019elliptic` | Weber, M., Domeniconi, G., Chen, J., Weidele, D. K. I., Bellei, C., Robinson, T., Leiserson, C. E. (2019). *Anti-Money Laundering in Bitcoin: Experimenting with Graph Convolutional Networks for Financial Forensics.* KDD 2019 Workshop on Anomaly Detection in Finance; arXiv:1908.02591. | VERIFIED | Releases the Elliptic dataset: >200K transactions, 234K edges, 166 features. **Random Forest beats GCN.** Supports the argument for strong classical baselines. |
| `elmougy2023elliptic` | Elmougy, Y., Liu, L. (2023). *Demystifying Fraudulent Transactions and Illicit Nodes in the Bitcoin Network for Financial Forensics.* Proc. KDD 2023, pp. 3979–3990. doi:10.1145/3580305.3599803; arXiv:2306.06108. | VERIFIED | Elliptic++: 822k wallet addresses with 56 features and 1.27M temporal interactions, for detecting both transactions and actors. |
| `deprez2026network` | Deprez, B., Vanderschueren, T., Baesens, B., Verdonck, T., Verbeke, W. (2026). *Network Analytics for Anti-money Laundering—A Systematic Literature Review and Experimental Evaluation.* INFORMS Journal on Data Science, 5(2), 119–154. doi:10.1287/ijds.2024.0042; arXiv:2405.19383. | VERIFIED | Review of 97 papers plus a standardised benchmark. Network features help. **GNNs need caution under class imbalance, and synthetic data can give overly optimistic results.** |
| `nasereddin2021alert` | Naser Eddin, A., Bono, J., Aparício, D., Polido, D., Ascensão, J. T., Bizarro, P., Ribeiro, P. (2021). *Anti-Money Laundering Alert Optimization Using Machine Learning with Graphs.* arXiv:2112.07508 [cs.LG]. | VERIFIED | An ML triage model on top of rule alerts, using real bank data. **Cuts false positives by 80% while keeping over 90% of true positives.** The reference for false-positive workload. |
| `vandenbeukel2026tide` | van den Beukel, M., Rožanec, J. M., Varbanescu, A.-L. (2026). *Tide: A Customisable Dataset Generator for Anti-Money Laundering Research.* arXiv:2603.01863 [cs.LG]. | VERIFIED | Generator with temporal laundering patterns. Model rankings depend on prevalence: LightGBM is best at 0.10% illicit (PR-AUC 78.05), XGBoost at 0.19% (85.12). Supports **gradient boosting as the baseline**. |
| `chung2025hybrid` | Chung, R., Sharma, P. N., Siponen, M., Vadodaria, R., Smith, L. (2025). *Hybrid Data can Enhance the Utility of Synthetic Data for Training Anti-Money Laundering Models.* ACFE Research Institute Annual Meeting 2024; arXiv:2509.18499. | VERIFIED | Adding public real-world features to synthetic AML data improves GNN utility while preserving privacy. |

LLM triage and SAR items (`torres2026triage`, `naik2025coinvestigator`, `naik2026llmops`, `pirmorad2025icl`) are listed in Section 1.

## 5. Regulation (official sources)

### 5.1 European Union (EU Publications Office, CELEX XHTML, read 2026-11-04)

- **`eu2024amlr`: Regulation (EU) 2024/1624** of 31 May 2024 on the prevention of the use of the financial system for the purposes of money laundering or terrorist financing (AMLR). OJ L, 2024/1624. https://eur-lex.europa.eu/eli/reg/2024/1624/oj. VERIFIED. Relevant provisions read:
  - **Art. 19:** when CDD applies (e.g., new business relationship; occasional transactions of at least EUR 10 000).
  - **Art. 20(1):** CDD measures, including (a) identifying and verifying the customer, and (b) identifying beneficial owners and understanding ownership and control.
  - **Art. 22:** minimum identification data, starting with "all names and surnames" for natural persons. This is relevant to name-variant matching.
  - **Art. 26:** ongoing monitoring of the relationship and transactions.
  - **Art. 76(5):** obliged entities may take decisions from automated processes, including profiling or AI systems, only if three conditions hold. (a) The data is limited to Chapter III CDD data. (b) Any decision to enter, refuse, maintain, or raise or lower CDD is subject to **"meaningful human intervention"**. (c) The customer can obtain an explanation and challenge it (except for suspicious-transaction reports).
  - **Application:** from **10 July 2027** (some entity types 10 July 2029).
  - **For the paper:** Art. 76(5) is the key hook for the explainability and human-in-the-loop metrics.
- **`eu2024amld6`: Directive (EU) 2024/1640** of 31 May 2024 on the mechanisms to be put in place by Member States for the prevention of the use of the financial system for the purposes of money laundering or terrorist financing (AMLD6). It amends Directive (EU) 2019/1937 and amends and repeals Directive (EU) 2015/849. VERIFIED.
  - Art. 10: central beneficial-ownership registers.
  - Art. 78: transposition by **10 July 2027**, with earlier dates for some articles.
- **`eu2024amla`: Regulation (EU) 2024/1620** of 31 May 2024 establishing the Authority for Anti-Money Laundering and Countering the Financing of Terrorism (AMLA), amending Regulations (EU) No 1093/2010, 1094/2010 and 1095/2010. VERIFIED.
  - Seat: Frankfurt am Main (Art. 4).
  - Applies from 1 July 2025, with some articles from 26 June 2024 (Art. 108).
- **`eu2024aiact`: Regulation (EU) 2024/1689** of 13 June 2024 (Artificial Intelligence Act). VERIFIED. What the text says for KYC:
  - **Annex III, point 1(a):** remote biometric identification is high-risk, but this **"shall not include AI systems intended to be used for biometric verification the sole purpose of which is to confirm that a specific natural person is the person he or she claims to be"**. 1:1 selfie-to-ID verification in eKYC is therefore outside point 1(a). Point 1(b) (biometric categorisation by sensitive attributes) and 1(c) (emotion recognition) remain high-risk.
  - **Annex III, point 5(b):** AI used to evaluate creditworthiness or establish credit scores of natural persons is high-risk, **"with the exception of AI systems used for the purpose of detecting financial fraud"**.
  - **Recital 58:** AI systems "provided for by Union law for the purpose of detecting fraud in the offering of financial services" should not be considered high-risk.
  - **Recital 59:** AI used by financial intelligence units for administrative AML analysis should not be classified as high-risk law-enforcement AI.
  - **What follows, and what does not:** Annex III does **not** list AML/KYC customer risk rating or sanctions screening as a high-risk use case. The text only explicitly excludes *fraud detection* from 5(b). Claims that "AML is excluded" should be worded precisely: AML/CDD is simply *not listed*. Unless such a system also performs credit scoring or remote biometric identification, it is not high-risk under Annex III, though Art. 50 transparency and GDPR / AMLR Art. 76 still apply.
- **`eu2026omnibus`: Regulation (EU) 2026/1744** of 8 July 2026 amending Regulation (EU) 2024/1689 (Digital Omnibus on AI). VERIFIED.
  - It defers Chapter III Sections 1–3 to **2 December 2027** for Annex III systems and **2 August 2028** for Annex I systems.
  - A text search found no change to the Annex III creditworthiness or biometric-verification wording.

### 5.2 FATF (official URLs read through Wayback snapshots; the live site returns 403)

- **`fatf2012rec`:** FATF (2012–2026). *International Standards on Combating Money Laundering and the Financing of Terrorism & Proliferation: The FATF Recommendations.* Adopted 16 February 2012, "Updated June 2026" (cover). Official PDF `fatf-gafi.org/content/dam/fatf-gafi/recommendations/fatf-recommendations-2012.pdf`, Wayback snapshot 2026-10-23. VERIFIED. Recommendations confirmed in the text:
  - **R.6:** targeted financial sanctions related to terrorism and terrorist financing.
  - **R.7:** proliferation TFS; it underpins Law 7262.
  - **R.10:** customer due diligence.
  - **R.15:** new technologies.
- **`fatf2021newtech`:** FATF (2021). *Opportunities and Challenges of New Technologies for AML/CFT.* FATF, Paris, July 2021 (cover). Snapshot 2026-10-11. VERIFIED. It discusses AI, machine learning and NLP as tools to improve monitoring and reduce manual review (Sections 3.x, incl. "Natural Language Processing and soft computing techniques").
- **`fatf2020digitalid`:** FATF (2020). *Guidance on Digital Identity.* FATF, Paris, March 2020 (cover; the page gives 6 March 2020). Snapshot 2025-10-07. VERIFIED.

### 5.3 Türkiye

- **`tr5549`: 5549 sayılı Suç Gelirlerinin Aklanmasının Önlenmesi Hakkında Kanun.** Accepted 11/10/2006; RG 18/10/2006, No. 26323. mevzuat.gov.tr/MevzuatMetin/1.5.5549.pdf. VERIFIED. **Art. 3 (Müşterinin tanınması):** obliged parties must identify those who carry out a transaction, and those on whose behalf it is carried out, before the transaction.
- **`tr_tedbirler2008`: Suç Gelirlerinin Aklanmasının ve Terörün Finansmanının Önlenmesine Dair Tedbirler Hakkında Yönetmelik** (Council of Ministers Decision 2007/13012). RG 09/01/2008, No. 26751. https://www.resmigazete.gov.tr/eskiler/2008/01/20080109-4.htm. VERIFIED (original text).
  - **Third Section "Müşterinin Tanınmasına İlişkin Esaslar":** Art. 5 says when identification is required; Art. 6 covers identification of natural persons (name, surname, place and date of birth, mother's and father's names, nationality, T.C. ID number, and so on).
  - **Caveat:** the thresholds in the original text are in YTL and the regulation has been amended several times (secondary sources mention amendments of 2023 and 13.02.2026). **Cite the consolidated text from mevzuat.gov.tr after checking it**; I could not retrieve it.
- **`bddk2021uzaktan`: Bankalarca Kullanılacak Uzaktan Kimlik Tespiti Yöntemlerine ve Elektronik Ortamda Sözleşme İlişkisinin Kurulmasına İlişkin Yönetmelik** (BDDK). RG 01/04/2021, No. 31441; in force 01/05/2021 (Art. 13). https://www.resmigazete.gov.tr/eskiler/2021/04/20210401-7.htm. VERIFIED (original text).
  - **Title correction:** the official title begins "Bankalarca Kullanılacak ...", not "Bankaların ...".
  - **Content:** a video call with a trained customer representative (Art. 5), a pre-call risk assessment (Art. 6), detailed documentation of document security features and verification criteria, and biometric data processed only with explicit consent.
  - **Caveat:** secondary sources report amendments in 2022 and 2023 (RG 25/05/2023, No. 32201), **not verified**.
- **`tr7262`: 7262 sayılı Kitle İmha Silahlarının Yayılmasının Finansmanının Önlenmesine İlişkin Kanun.** Accepted 27/12/2020; RG 31/12/2020, No. 31351 (5th repeat issue). VERIFIED. It implements UN Security Council proliferation-financing sanctions decisions (asset freezing).
- **`tr6415`: 6415 sayılı Terörizmin Finansmanının Önlenmesi Hakkında Kanun.** Accepted 07/02/2013; RG 16/02/2013, No. 28561. VERIFIED. It implements the 1999 Convention and UN Security Council decisions; provides asset freezing.
- **Data-localisation hooks (the on-premise argument):**
  - **`tr6698`: 6698 sayılı Kişisel Verilerin Korunması Kanunu**, RG 07/04/2016, No. 29677. **Art. 9** (transfer abroad) was rewritten by Law 7499 (02/03/2024). VERIFIED.
  - **`bddk2020bs`: Bankaların Bilgi Sistemleri ve Elektronik Bankacılık Hizmetleri Hakkında Yönetmelik**, RG 15/03/2020, No. 31069. **Art. 25(1):** banks must keep primary and secondary systems in Türkiye. **Art. 25(5):** this extends to outsourced and cloud services. VERIFIED (original text). **This is the legal basis for "the model must run domestically or on-premise".**

## 6. Method references (preregistration in NLP)

| Key | Reference | Status | Summary |
|---|---|---|---|
| `vanmiltenburg2021prereg` | van Miltenburg, E., van der Lee, C., Krahmer, E. (2021). *Preregistering NLP research.* Proc. NAACL-HLT 2021, pp. 613–623. doi:10.18653/v1/2021.naacl-main.51; arXiv:2103.06944. | VERIFIED | Proposes preregistration questions for NLP studies and argues for registered reports. |
| `sogaard2023prereg` | Søgaard, A., Hershcovich, D., de Lhoneux, M. (2023). *A Two-Sided Discussion of Preregistration of NLP Research.* Proc. EACL 2023, pp. 83–93. doi:10.18653/v1/2023.eacl-main.6; arXiv:2302.10086. | VERIFIED | Pros and cons of preregistration (HARKing, confirmatory bias, flag-planting, and so on). Cite it to show the design is aware of the critiques. |

---

## 7. Table of verified references (summary)

| # | Key | Year | Type | Identifier | Status |
|---|---|---|---|---|---|
| 1 | chernakov2025adverse | 2025 | arXiv | 2602.23373 | V |
| 2 | khandpur2020adverse | 2020 | KDD-W / arXiv | 2110.11542 | V |
| 3 | wahib2026spectra | 2026 | arXiv | 2609.25474 | V |
| 4 | he2025aria | 2025 | EMNLP Ind. | 10.18653/v1/2025.emnlp-industry.115 | V |
| 5 | naik2025coinvestigator | 2025 | arXiv | 2509.08380 | V |
| 6 | torres2026triage | 2026 | arXiv | 2604.19755 | V |
| 7 | naik2026llmops | 2026 | arXiv | 2605.11232 | V |
| 8 | pirmorad2025icl | 2025 | ICDMW | 10.1109/ICDMW69685.2025.00026 | V |
| 9 | koletsis2024corruption | 2024 | arXiv | 2409.13704 | V |
| 10 | pavlidis2023ai | 2023 | JMLC | 10.1108/JMLC-03-2023-0050 | V |
| 11 | reite2024client | 2024 | JMLC | 10.1108/JMLC-03-2024-0040 | V |
| 12 | han2020aml | 2020 | Digital Finance | 10.1007/s42521-020-00023-1 | V-meta |
| 13 | chen2018mlaml | 2018 | KAIS | 10.1007/s10115-017-1144-z | V-meta |
| 14 | smith2026opensanctions | 2026 | arXiv | 2603.11051 | V |
| 15 | chourasia2026sger | 2026 | ACL Ind. | 10.18653/v1/2026.acl-industry.101 | V |
| 16 | gopal2026crossscript | 2026 | arXiv | 2610.31407 | V |
| 17 | gupta2026corpfam | 2026 | arXiv | 2609.04269 | V |
| 18 | zeakis2026distiller | 2026 | arXiv | 2602.05452 | V |
| 19 | li2024booster | 2024 | WWW Comp. | 10.1145/3589335.3651245 | V |
| 20 | fellegi1969theory | 1969 | JASA | 10.1080/01621459.1969.10501049 | V-meta |
| 21 | jaro1989advances | 1989 | JASA | 10.1080/01621459.1989.10478785 | V-meta |
| 22 | christen2012datamatching | 2012 | Book | 10.1007/978-3-642-31164-2 | V-meta |
| 23 | bilenko2003adaptive | 2003 | IEEE IS | 10.1109/MIS.2003.1234765 | V-meta |
| 24 | pouliquen2005multilingual | 2005 | Corela | 10.4000/corela.1219 | V-meta |
| 25 | ofac_sdn | — | Web (official) | ofac.treasury.gov | V |
| 26 | eu_fsf_list | — | Web (official) | data.europa.eu | V |
| 27 | un_sc_list | — | Web (official) | main.un.org | V |
| 28 | opensanctions_default | — | Web (dataset) | opensanctions.org | V |
| 29 | arlazarov2019midv500 | 2019 | Computer Optics | 10.18287/2412-6179-2019-43-5-818-824 | V |
| 30 | bulatov2020midv2019 | 2020 | SPIE ICMV | 10.1117/12.2558438 | V |
| 31 | bulatov2022midv2020 | 2022 | Computer Optics | 10.18287/2412-6179-CO-1006 | V |
| 32 | guan2024idnet | 2024 | arXiv | 2408.01690 | V |
| 33 | korshunov2025fantasyid | 2025 | IJCB | 10.1109/IJCB65343.2025.11411292 | V |
| 34 | zhao2026docforge | 2026 | arXiv | 2603.01433 | V |
| 35 | kumar2026flid | 2026 | arXiv | 2605.09089 | V |
| 36 | das2026idsurvey | 2026 | arXiv | 2607.01442 | V |
| 37 | vinogradov2025forge | 2025 | arXiv | 2601.00829 | V |
| 38 | xu2026docprivacy | 2026 | ACM MM / arXiv | 2608.12911 | V (DOI pending) |
| 39 | amada2025ekyc | 2025 | FG / arXiv | 2507.22601 | V |
| 40 | bai2025qwen3vl | 2025 | arXiv | 2511.21631 | V |
| 41 | li2025dotsocr | 2025 | arXiv | 2512.02498 | V |
| 42 | liu2024ocrbench | 2024 | Sci China Inf Sci | 10.1007/s11432-024-4235-6 | V |
| 43 | altman2023amlworld | 2023 | NeurIPS D&B | 10.52202/075280-1300 | V |
| 44 | oztas2023samld | 2023 | IEEE ICEBE | 10.1109/ICEBE59045.2023.00028 | V-meta |
| 45 | lopezrojas2018paysim | 2018 | IJSPM | 10.1504/IJSPM.2018.093756 | V-meta |
| 46 | weber2019elliptic | 2019 | KDD-W / arXiv | 1908.02591 | V |
| 47 | elmougy2023elliptic | 2023 | KDD | 10.1145/3580305.3599803 | V |
| 48 | deprez2026network | 2026 | INFORMS JDS | 10.1287/ijds.2024.0042 | V |
| 49 | nasereddin2021alert | 2021 | arXiv | 2112.07508 | V |
| 50 | vandenbeukel2026tide | 2026 | arXiv | 2603.01863 | V |
| 51 | chung2025hybrid | 2025 | arXiv | 2509.18499 | V |
| 52 | vanmiltenburg2021prereg | 2021 | NAACL | 10.18653/v1/2021.naacl-main.51 | V |
| 53 | sogaard2023prereg | 2023 | EACL | 10.18653/v1/2023.eacl-main.6 | V |
| 54 | eu2024amlr | 2024 | EU Reg. | CELEX 32024R1624 | V |
| 55 | eu2024amld6 | 2024 | EU Dir. | CELEX 32024L1640 | V |
| 56 | eu2024amla | 2024 | EU Reg. | CELEX 32024R1620 | V |
| 57 | eu2024aiact | 2024 | EU Reg. | CELEX 32024R1689 | V |
| 58 | eu2026omnibus | 2026 | EU Reg. | CELEX 32026R1744 | V |
| 59 | fatf2012rec | 2012–2026 | FATF | Rec. (upd. June 2026) | V (Wayback) |
| 60 | fatf2021newtech | 2021 | FATF | July 2021 | V (Wayback) |
| 61 | fatf2020digitalid | 2020 | FATF | March 2020 | V (Wayback) |
| 62 | tr5549 | 2006 | TR Law | RG 26323 | V |
| 63 | tr_tedbirler2008 | 2008 | TR Reg. | RG 26751 | V (original) |
| 64 | bddk2021uzaktan | 2021 | TR Reg. | RG 31441 | V (original) |
| 65 | tr7262 | 2020 | TR Law | RG 31351 | V |
| 66 | tr6415 | 2013 | TR Law | RG 28561 | V |
| 67 | tr6698 | 2016 | TR Law | RG 29677 | V |
| 68 | bddk2020bs | 2020 | TR Reg. | RG 31069 | V (original) |

**Totals:** 68 items. 57 are fully verified (abstract or legal text read), including 3 FATF documents read through Wayback snapshots of the official URLs and 3 Turkish regulations checked only in their original Resmî Gazete text. 11 are verified at metadata level only.

**Not found or not verified:**
- the original PaySim EMSS 2016 paper (not in Crossref);
- the SAML-D size and typology figures;
- the consolidated MASAK Tedbirler and BDDK remote-ID texts;
- the live fatf-gafi.org site (403);
- the Crossref record for the ACM MM 2026 DOI (not yet registered);
- the OpenSanctions licence terms.

---

## 8. Gap and contribution

### What existing work does not do

1. **No preregistered, multi-task comparison on public KYC data.**
   - Existing LLM-for-KYC work is single-task and mostly uses proprietary data. This covers adverse media (Chernakov et al.), document processing (Spectra), name matching (SGER, ARIA at TikTok Pay), and triage and SAR drafting (Torres et al., Co-Investigator).
   - Only OpenSanctions Pairs and Torres et al. compare LLMs against rule or classical baselines on **public** data, and each covers only one task. None was preregistered.
   - No study evaluates one model family across the CDD chain:
     - name and sanctions screening,
     - ID-document field extraction,
     - adverse media,
     - risk rating with explanation,
     - alert triage.
2. **No measurement of false-positive workload and cost as primary outcomes.**
   - Most papers report F1 or accuracy. Workload is reported only in production case studies (Spectra: 96% less review; Naser Eddin et al.: 80% fewer false positives).
   - None reports, under the same protocol, analyst-hours or alerts per true hit at fixed recall, plus token and GPU cost per decision, for open local models against Jaro–Winkler, Fellegi–Sunter or gradient boosting.
3. **No Turkish or Turkic cross-script names.**
   - The cross-script evidence covers Latin/Cyrillic/Arabic in aggregate (OpenSanctions Pairs) or Indic scripts (Gopal et al., SGER).
   - Nobody tests Turkish-specific phenomena: dotted/dotless i, ğ/ş/ç folding, Arabic-origin names romanised in Turkish versus English or French conventions, and Cyrillic renderings of Turkic names.
4. **No on-premise or data-localisation framing.**
   - OpenSanctions Pairs notes that a 14B distilled model is "locally deployable", and the LLMOps paper self-hosts. But no study ties model choice to a binding localisation rule such as BDDK Art. 25 (primary and secondary systems in Türkiye) or KVKK Art. 9.
   - No study ties explainability to the AMLR Art. 76(5) human-intervention and explanation duty.
5. **No open-VLM evaluation on MIDV-2020.**
   - The ID-document literature covers detection and forgery: FantasyID, IDNet, DOCFORGE-BENCH, FLiD.
   - Field extraction with current open VLMs (Qwen3-VL, dots.ocr) against classical OCR baselines on MIDV-2020 is absent. Hallucinated fields are a documented risk (Xu et al.).
6. **Explanations are not checked against the regulatory decision.** Torres et al. measure faithfulness for triage only. Nobody checks whether an LLM's CDD risk explanation cites the right FATF R.10 or AMLR Art. 20 factor.

### Candidate contribution statements

1. **Benchmark and preregistered test.** We give the first preregistered, multi-task evaluation of open, domestically or locally hosted LLMs and VLMs on public KYC/CDD tasks. The tasks are sanctions name screening (OpenSanctions/OFAC/EU/UN), ID-document field extraction (MIDV-2020), adverse-media classification, and alert triage (AMLworld/SAML-D). Every model is compared with the classical baseline a bank would actually run: Jaro–Winkler and Fellegi–Sunter, Tesseract-class OCR, and gradient boosting. This shows **where LLMs add value over existing rules and where they do not**, for compliance and model-risk teams.
2. **Workload and cost, not only accuracy.** We report false positives per true hit at regulator-relevant recall levels, estimated analyst review load, and per-decision compute cost on on-premise hardware. This turns model scores into the **operational trade-off a bank faces under AMLR Art. 76(5) human-intervention requirements**.
3. **Cross-script and Turkish stress test plus a localisation-compliant design.** We add a controlled Turkish/Arabic/Cyrillic transliteration stratum and test whether calibration fixes the documented cross-script recall collapse. We frame the whole pipeline around BDDK Art. 25 and KVKK Art. 9. This gives **banks in data-localisation jurisdictions** evidence on what can be done without sending customer data abroad.

### Close prior work that threatens novelty

- **Smith et al. (2026), OpenSanctions Pairs, arXiv:2603.11051.** A public sanctions entity-matching benchmark that already compares a rule baseline with open and closed LLMs, includes a locally deployable model, and identifies cross-script transliteration as the LLM failure mode. **The name-matching sub-study must not be pitched as the first LLM-vs-rules sanctions comparison.** Position it as using that benchmark or extending it: a Turkish stratum, workload/cost at fixed recall, current open models, and preregistration.
- **Torres et al. (2026), arXiv:2604.19755.** LLM AML triage on public synthetic benchmarks against rule, tabular and graph baselines, with explanation-faithfulness metrics. This overlaps with any triage or explainability sub-study.
- **Gopal et al. (2026), arXiv:2610.31407.** Already shows cross-script same-person collapse and the calibration fix in LLMs, for Indic scripts. A Turkish replication is incremental unless framed as a KYC-operational test.
- **Wahib et al. (2026, Spectra) and Chourasia et al. (2026, SGER, ACL Industry).** Show production KYC document and name-matching LLM pipelines, but on proprietary data. Our public-data, reproducible angle remains distinct.
- **Not found:** any paper that combines several KYC tasks, open on-premise models, classical baselines, preregistration, and a workload/cost outcome. The combination, not any single task, is the defensible novelty.
