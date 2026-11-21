#!/bin/bash
# Mehmet 04.11.2026: yerelde yalniz qwen3.8:27b pilotu bitsin; sonra EVREN'e gecis.
# qwen bitince DURAKLAT (EVREN yeni istek gondermez), yoldaki EVREN istekleri biter, surec durdurulur,
# yalniz EVREN modelleriyle yeniden baslatilir (devam ettirilebilir kosu).
cd "$(dirname "$0")/.."
LOG=$(ls -t logs/pilot_2026*.log | tail -1)
PID=$(cat logs/kos.pid)
until grep -q "\[qwen3.8:27b-mxfp8\] bitti" "$LOG"; do sleep 15; done
echo "$(date '+%F %T') qwen yerel bitti -> DURAKLAT"
touch DURAKLAT
# yoldaki EVREN istekleri: run dosyalari 7 dk boyunca degismeyene ya da 12 dk dolana kadar bekle
bas=$(date +%s)
while true; do
  son=$(stat -f %m data/runs/pilot/deepseek-v4.1-flash.jsonl data/runs/pilot/qwen3.8-flash-next.jsonl data/runs/pilot/gemma-4-31b.jsonl data/runs/pilot/glm-5.3.jsonl | sort -n | tail -1)
  now=$(date +%s)
  if [ $((now - son)) -ge 420 ] || [ $((now - bas)) -ge 720 ]; then break; fi
  sleep 20
done
echo "$(date '+%F %T') surec durduruluyor: $PID"
CH=$(pgrep -P "$PID"); kill $CH "$PID" 2>/dev/null; sleep 5
mkdir -p data/runs/pilot_iptal
for f in data/runs/pilot/gemma4_31b.jsonl data/runs/pilot/gpt-oss_20b.jsonl; do [ -f "$f" ] && mv "$f" data/runs/pilot_iptal/; done
rm -f DURAKLAT
TS=$(date +%Y%m%d_%H%M)
nohup caffeinate -i ~/.venv/bin/python3 -I deney/kos.py --set pilot --models deepseek-v4.1-flash,qwen3.8-flash-next,gemma-4-31b,glm-5.3 --workers 12 > logs/pilot_evren_$TS.log 2>&1 &
echo $! > logs/kos.pid
echo "$(date '+%F %T') EVREN pilotu yeniden baslatildi: $(cat logs/kos.pid) -> logs/pilot_evren_$TS.log"
