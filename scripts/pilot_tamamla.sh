#!/bin/bash
# Pilot EVREN kosusu bitince hatali (503 vb.) satirlari yeniden dene; en fazla 6 tur, turlar arasi 10 dk.
cd "$(dirname "$0")/.."
PID=$(cat logs/kos.pid)
while kill -0 "$PID" 2>/dev/null; do sleep 30; done
for tur in 1 2 3 4 5 6; do
  hata=$(~/.venv/bin/python3 -I - <<'PY'
import glob, json
n = 0
for fp in glob.glob("data/runs/pilot/*.jsonl"):
    if "27b-mxfp8" in fp:
        continue
    son = {}
    for l in open(fp):
        r = json.loads(l)
        if not r.get("error") or r["tid"] not in son:
            son[r["tid"]] = r
    n += sum(1 for r in son.values() if r.get("error"))
print(n)
PY
)
  echo "$(date '+%F %T') tur $tur: hatali gorev $hata"
  [ "$hata" = "0" ] && break
  sleep 600
  TS=$(date +%Y%m%d_%H%M)
  caffeinate -i ~/.venv/bin/python3 -I deney/kos.py --set pilot --models deepseek-v4.1-flash,qwen3.8-flash-next,gemma-4-31b,glm-5.3 --workers 12 > logs/pilot_evren_$TS.log 2>&1
done
echo "$(date '+%F %T') PILOT_TAMAM"
