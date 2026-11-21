#!/usr/bin/env python3
"""LLM alarm ayiklama kosusu (devam ettirilebilir). Her EVREN modeli ayri is parcaciginda; yerel modeller sirayla.

  ~/.venv/bin/python3 -I deney/kos.py --set pilot
  ~/.venv/bin/python3 -I deney/kos.py --set pilot --models gemma-4-31b --limit 5
Gorevler: F alarmlari + E kanali alarmlari (E_TAU, data/e_tau.json'dan). Cikti: data/runs/<set>/<model>.jsonl
Hatali satirlar bir sonraki baslatmada yeniden denenir.
"""
import argparse, json, os, random, sys, threading

KOK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(KOK, "deney"))
import llmclient as L  # noqa: E402
import karar as K  # noqa: E402

EVREN = ["deepseek-v4.1-flash", "qwen3.8-flash-next", "gemma-4-31b", "glm-5.3"]
YEREL = ["qwen3.8:27b-mxfp8", "gemma4:31b", "gpt-oss:20b"]
GLM_PILOT = 150
KARARLAR = {"ESCALATE": "escalate", "DISCOUNT": "discount"}


def gorevler(set_):
    W, C, KA = K.yukle(set_)
    tau = json.load(open(os.path.join(KOK, "data", "e_tau.json")))["e_tau"]
    out = []
    for cid, cands in KA.items():
        for a in K.alarmlar(cands, "FE", e_tau=tau):
            out.append({"tid": f"{cid}|{a['eid']}", "cid": cid, "eid": a["eid"], "f": a["f"], "e": a["e"]})
    return out, W, C


def cagir_fn(W, C):
    def f(t, model):
        c, e = C[t["cid"]], W[t["eid"]]
        mt = 1500 if model.startswith("glm") else (600 if model.startswith("gpt-oss") else 300)
        r = L.chat(model, K.istem(c, e), max_tokens=mt, temperature=0.0, json_mode=True, timeout=400)
        j = L.parse_json(r["text"])
        dec = KARARLAR.get(str((j or {}).get("decision", "")).strip().upper())
        res = {"tid": t["tid"], "model": model, "cid": t["cid"], "eid": t["eid"],
               "decision": dec, "name_assessment": (j or {}).get("name_assessment"),
               "dob_assessment": (j or {}).get("dob_assessment"), "reason": (j or {}).get("reason"),
               "parsed": dec is not None, "raw": None if dec else (r["text"] or "")[:500],
               "latency_s": r["latency_s"], "in_tok": r["in_tok"], "out_tok": r["out_tok"],
               "served_model": r.get("served_model"), "hesap": r.get("hesap"), "error": r["error"]}
        return res
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="pilot", choices=["pilot", "full"])
    ap.add_argument("--models", default=",".join(EVREN + YEREL))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    tasks, W, C = gorevler(a.set)
    if a.limit:
        tasks = tasks[:a.limit]
    print(f"{len(tasks)} alarm gorevi", flush=True)
    outdir = os.path.join(KOK, "data", "runs", a.set)
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(KOK, ".duraklat_destekli"), "w").close()
    fn = cagir_fn(W, C)
    ms = a.models.split(",")
    ev, yr = [m for m in ms if L.backend_of(m) == "evren"], [m for m in ms if L.backend_of(m) == "ollama"]

    def tek(m, w):
        ts = tasks
        if a.set == "pilot" and m.startswith("glm"):
            ts = random.Random(7).sample(tasks, min(GLM_PILOT, len(tasks)))  # on kayit: glm pilotta alt orneklem
        L.run_tasks(ts, m, os.path.join(outdir, f"{m.replace(':', '_')}.jsonl"), fn, workers=w, log_every=50)

    ths = [threading.Thread(target=tek, args=(m, 6 if m.startswith("glm") else a.workers)) for m in ev]
    if yr:
        ths.append(threading.Thread(target=lambda: [tek(m, 2) for m in yr]))
    for t in ths:
        t.start()
    for t in ths:
        t.join()


if __name__ == "__main__":
    main()
