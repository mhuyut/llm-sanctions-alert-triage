#!/usr/bin/env python3
"""Kesifsel: LLM'lerin kacirdigi pozitiflerin nedeni (F hatti, kurulum hatasi dislanmis kume) -> data/stats_hata_full.json

  ~/.venv/bin/python3 -I scripts/hata_turleri.py
Neden, modelin kendi kaydi (pozitifin kendi listesi kaydi) icin verdigi degerlendirmeden okunur:
dob_conflict (tarih celiskisi dedi), name_different (farkli ad dedi), inconsistent (ad ayni/varyant ve tarih uyumlu/kucuk
fark dedi ama yine de eledi). Ad kosulu ve tarih kosulu kirilimlari da yazilir.
"""
import json, os, sys
from collections import Counter

KOK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(KOK, "deney"))
import karar as K  # noqa: E402
from dob import durum  # noqa: E402

SET = "full"
LLM = ["deepseek-v4.1-flash", "qwen3.8-flash-next", "gemma-4-31b"]


def main():
    W, C, KA = K.yukle(SET)
    out = {}
    for m in LLM:
        d = {}
        for l in open(os.path.join(KOK, "data", "runs", SET, f"{m}.jsonl"), encoding="utf-8"):
            x = json.loads(l)
            if not x.get("error") or x["tid"] not in d:
                d[x["tid"]] = x
        neden, ad, tarih, n = Counter(), Counter(), Counter(), 0
        for cid, c in C.items():
            als = K.alarmlar(KA[cid], "F")
            if K.musteri_dogru(c, als, W) != "escalate" or durum(c["dob"], W[c["truth"]["eid"]]["dobs"]) == "conflict":
                continue
            n += 1
            rs = [d.get(f"{cid}|{a['eid']}") for a in als]
            if any(not x or not x.get("decision") or x["decision"] == "escalate" for x in rs):
                continue
            own = next(x for a, x in zip(als, rs) if W[a["eid"]]["cluster"] == c["truth"]["cluster"])
            if own.get("dob_assessment") == "conflict":
                k = "dob_conflict"
            elif own.get("name_assessment") == "different":
                k = "name_different"
            else:
                k = "inconsistent"
            neden[k] += 1
            ad[c["truth"]["cell"].split("|")[0]] += 1
            tarih[c["truth"]["cell"].split("|")[1]] += 1
        out[m] = {"n_pos": n, "missed": sum(neden.values()), "reason": dict(neden), "by_name": dict(ad), "by_dob": dict(tarih)}
        print(m, out[m])
    json.dump(out, open(os.path.join(KOK, "data", f"stats_hata_{SET}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
