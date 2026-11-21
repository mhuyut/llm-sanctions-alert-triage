#!/usr/bin/env python3
"""1. asama: aday uretimi (screening). data/candidates_<set>.jsonl

Her musteri icin izleme listesindeki kayitlar iki kanalla puanlanir:
  F: bulanik ad eslestirme, rapidfuzz token_set_ratio, normalize latin adlar uzerinde; kayit puani = adlarinin en yuksegi
  E: yerel bge-m3 gomme (Ollama, localhost) kosinus benzerligi; tum adlar (latin + latin disi); kayit puani = en yuksek
Kaydedilen adaylar: F >= 70 olanlar ve E'de ilk 5 (sonradan esik analizi icin). Alarm tanimi on kayittadir
(F >= 85 ilk 5; E kanali esigi pilotta secilir).
Puanlayici ve esik pilot tarama ciktisina bakilarak secildi (WRatio >= 85 genel nufusun %53'unde alarm uretiyordu).

Calistirma: ~/.venv/bin/python3 -I deney/tarama.py --set pilot
"""
import argparse, hashlib, json, os, sys, time, urllib.request

import numpy as np
from rapidfuzz import fuzz, process

KOK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(KOK, "deney"))
from adlar import norm  # noqa: E402

F_KAYIT = 70
E_ILK = 5
EMB_MODEL = "bge-m3"


def embed(texts, cache):
    """Ollama /api/embed, onbellekli (data/emb_cache/<sha>.npy)."""
    os.makedirs(cache, exist_ok=True)
    out = [None] * len(texts)
    todo = []
    for i, t in enumerate(texts):
        p = os.path.join(cache, hashlib.sha1(t.encode()).hexdigest() + ".npy")
        if os.path.exists(p):
            out[i] = np.load(p)
        else:
            todo.append(i)
    for s in range(0, len(todo), 64):
        idx = todo[s:s + 64]
        body = json.dumps({"model": EMB_MODEL, "input": [texts[i] for i in idx]}).encode()
        for k in range(5):
            try:
                req = urllib.request.Request("http://localhost:11434/api/embed", data=body,
                                             headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=300) as r:
                    vs = json.load(r)["embeddings"]
                break
            except Exception as e:
                print("embed hata", repr(e)[:120], flush=True)
                time.sleep(5 * (k + 1))
        else:
            raise RuntimeError("embed basarisiz")
        for i, v in zip(idx, vs):
            v = np.asarray(v, dtype=np.float32)
            v /= np.linalg.norm(v) + 1e-9
            np.save(os.path.join(cache, hashlib.sha1(texts[i].encode()).hexdigest() + ".npy"), v)
            out[i] = v
        if (s // 64) % 20 == 0:
            print(f"  gomme {s + len(idx)}/{len(todo)}", flush=True)
    return np.vstack(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["pilot", "full"], required=True)
    a = ap.parse_args()
    W = [json.loads(l) for l in open(os.path.join(KOK, "data", "watchlist.jsonl"), encoding="utf-8")]
    C = [json.loads(l) for l in open(os.path.join(KOK, "data", f"customers_{a.set}.jsonl"), encoding="utf-8")]
    # ad -> kayit indeksi
    lat_ad, lat_e, tum_ad, tum_e = [], [], [], []
    for j, e in enumerate(W):
        for n in e["names"]:
            if n["script"] == "latin":
                lat_ad.append(norm(n["name"]))
                lat_e.append(j)
            tum_ad.append(n["name"])
            tum_e.append(j)
    lat_e, tum_e = np.array(lat_e), np.array(tum_e)
    lat_bas = np.r_[0, np.nonzero(np.diff(lat_e))[0] + 1]
    tum_bas = np.r_[0, np.nonzero(np.diff(tum_e))[0] + 1]
    assert len(lat_bas) == len(W) == len(tum_bas)
    q = [norm(c["name"]) for c in C]
    t0 = time.time()
    F = np.zeros((len(C), len(W)), dtype=np.uint8)
    for s in range(0, len(C), 2000):
        m = process.cdist(q[s:s + 2000], lat_ad, scorer=fuzz.token_set_ratio, dtype=np.uint8, workers=-1)
        F[s:s + 2000] = np.maximum.reduceat(m, lat_bas, axis=1)  # kayit bazinda en yuksek (adlar kayit sirasinda)
    print(f"F kanali {time.time() - t0:.0f} sn", flush=True)
    cache = os.path.join(KOK, "data", "emb_cache")
    t0 = time.time()
    EW = embed(tum_ad, cache)
    EC = embed([c["name"] for c in C], cache)
    print(f"gomme {time.time() - t0:.0f} sn", flush=True)
    out = open(os.path.join(KOK, "data", f"candidates_{a.set}.jsonl"), "w", encoding="utf-8")
    for s in range(0, len(C), 1000):
        S = EC[s:s + 1000] @ EW.T
        E = np.maximum.reduceat(S, tum_bas, axis=1)
        for k in range(S.shape[0]):
            i = s + k
            top_e = np.argsort(-E[k])[:E_ILK]
            f_idx = np.nonzero(F[i] >= F_KAYIT)[0]
            idx = sorted(set(f_idx.tolist()) | set(top_e.tolist()), key=lambda j: (-int(F[i, j]), -float(E[k, j])))
            rec = {"cid": C[i]["cid"], "cands": [{"eid": W[j]["eid"], "f": int(F[i, j]), "e": round(float(E[k, j]), 4),
                                                  "e_rank": int((E[k] > E[k, j]).sum()) + 1} for j in idx]}
            out.write(json.dumps(rec) + "\n")
    out.close()
    print("yazildi", a.set, len(C), flush=True)


if __name__ == "__main__":
    main()
