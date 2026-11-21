#!/bin/sh
# Download the two official sanctions lists used in the study into data/raw/ and compare them with the
# study snapshot (data/raw/SHA256SUMS, taken 2026-11-04T10:05:06Z). The lists are updated often, so a
# fresh download will normally NOT match the snapshot hashes; the study's own watch list cannot be
# rebuilt byte for byte from a later download. All model outputs in data/runs/ refer to list entries by
# their internal id (eid), so every number in the paper can be recomputed without the lists.
#
#   sh scripts/listeleri_indir.sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p data/raw
# UK Sanctions List (FCDO), Open Government Licence v3.0 (personal data excluded from the licence)
curl -fsSL -o data/raw/UK-Sanctions-List.xml https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.xml
curl -fsSL -o data/raw/UK-Sanctions-List.csv https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.csv
# EU consolidated financial sanctions list (FSF), Commission reuse notice (Decision 2011/833/EU)
curl -fsSL -o data/raw/EU-FSF-full.xml "https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw"
echo "Comparison with the study snapshot (mismatch is expected for a later download):"
(cd data/raw && shasum -a 256 -c SHA256SUMS) || true
echo "Next: python3 deney/liste.py   # -> data/watchlist.jsonl"
