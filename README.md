# Can Open LLMs Clear Sanctions-Screening Alerts? — replication package

Code, data and model outputs for the paper *Can Open LLMs Clear Sanctions-Screening Alerts? A
Pre-registered Test on Public Sanctions Lists with Turkish Name Variants* (Mehmet Murat Huyut, arXiv 2026).

Paper: arXiv link will be added after announcement.

All numbers in the paper are computed from the files in this package by the analysis scripts below,
**without calling any model API**. Re-running the experiment itself requires an OpenAI-compatible
endpoint serving the models (see "Re-running the experiment").

## Layout

| Path | Content |
|---|---|
| `deney/politika.md` | The written level-1 disposition policy given, word for word, to the models and to the rule baselines. |
| `deney/liste.py` | Parses the UK Sanctions List and the EU consolidated list into the watch list (natural persons with a date of birth). |
| `deney/adlar.py`, `deney/dob.py` | Name normalisation and variant generators (Turkish spellings, romanisations, word order, typos); date-of-birth comparison. |
| `deney/musteri.py` | Generates the synthetic customers (pilot and full sets from disjoint persons). |
| `deney/tarama.py` | Stage-1 screening: fuzzy channel (token_set_ratio ≥ 85) and embedding channel (bge-m3). |
| `deney/karar.py` | Alert definition, ground truth, rule baselines R0–R2 and the LLM prompt. |
| `deney/kos.py`, `deney/llmclient.py` | Resumable runner and minimal OpenAI-compatible client (keys are read from files, never from code). |
| `data/customers_*.jsonl` | The 2,220 pilot and 12,200 full synthetic customers, with their ground-truth cell. |
| `data/candidates_*.jsonl` | Stage-1 candidates per customer (fuzzy score, embedding similarity and rank). |
| `data/e_tau.json` | Embedding threshold chosen on the pilot by the pre-registered rule (`scripts/tau.py`). |
| `data/runs/full/*.jsonl` | Every model decision on the 7,383 full-set alerts (decision, name and date assessment, rationale, tokens, latency). |
| `data/runs/pilot/*.jsonl` | Pilot outputs, including glm-5.3, which failed the parse gate, and the exploratory local qwen3.8 run. |
| `data/stats_*.json`, `data/hipotez_full.json`, `data/stats_hata_full.json` | All numbers used in the paper. |
| `data/raw/SHA256SUMS`, `data/raw/DOWNLOAD_DATE` | Hashes and timestamp of the official list snapshots used (2026-11-04). |
| `logs/usage.jsonl` | Token counts per call (account index only), used for the cost figures. |
| `preregistration/` | The pre-registration with both amendments and the deviation note, and the SHA-256 hashes taken before the pilot and at each change. |
| `literature_scan.md` | Literature scan with the verification status of each source. |
| `MANIFEST.sha256` | Hash of every file in this package. |

## The watch list

The official list files are not redistributed. `scripts/listeleri_indir.sh` downloads them from the
UK FCDO and the European Commission, and `python3 deney/liste.py` rebuilds `data/watchlist.jsonl`.
The lists change often, so a later download will not reproduce the study snapshot exactly; the
snapshot hashes are in `data/raw/SHA256SUMS` and the hash of the derived watch list is in
`preregistration/onkayit_sha256.txt`.

UK Sanctions List: contains public sector information licensed under the Open Government Licence v3.0.
EU consolidated financial sanctions list: © European Union, reuse authorised under Commission
Decision 2011/833/EU. Both lists contain personal data published for compliance purposes; use them only
for that kind of purpose and in line with the applicable data-protection law.

## Reproducing the paper's numbers (no API needed)

Python 3.11+, with `rapidfuzz`, `scipy`, `statsmodels`, `lxml`:

```bash
pip install rapidfuzz scipy statsmodels lxml
python3 scripts/analiz.py full        # -> data/stats_full.json (alerts, recall, disposition, model statistics)
python3 scripts/hipotez.py full       # -> data/hipotez_full.json (pre-registered tests H1–H6, deviation sensitivity)
python3 scripts/hata_turleri.py       # -> data/stats_hata_full.json (exploratory error types)
```

The analysis needs `data/watchlist.jsonl` (see "The watch list").

Checking the pre-registration (from the package root; the hash file is kept verbatim, so the path of
the hypotheses document is rewritten from the original `makale/` folder to `preregistration/`). The
last of the four hashes of the hypotheses document is the current version:

```bash
grep -v '^#' preregistration/onkayit_sha256.txt | sed 's#  makale/#  preregistration/#; s#  \#.*##'
```

## Re-running the experiment

The study used three open-weight models (deepseek-v4.1-flash, qwen3.8-flash-next, gemma-4-31b) served
by a domestic (Turkish) research API with an OpenAI-compatible interface, at temperature 0 with a fixed
seed and reasoning disabled. `deney/llmclient.py` reads one key per model from files named
`.api_key_evren*` in `KEY_DIR`; edit `KEY_DIR` to point at your own key files, or adapt the client to
any OpenAI-compatible endpoint. Then:

```bash
sh scripts/listeleri_indir.sh && python3 deney/liste.py
python3 deney/musteri.py --set full
python3 deney/tarama.py --set full
python3 deney/kos.py --set full                                   # resumable
python3 deney/kos.py --set pilot --models gemma-4-31b --limit 5   # smoke test
```

## License

Code (`*.py`): MIT. Data, policy, synthetic customers, model outputs and documents: CC BY 4.0.
See `LICENSE`. The official sanctions lists keep their own terms (above).

## Citation

See `CITATION.cff`.
