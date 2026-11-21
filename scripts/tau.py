#!/usr/bin/env python3
"""E kanali esigi (on kayit kurali): pilotta genel nufus musterileri basina ortalama E'ye ozgu alarm <= 0.10 olan
0.01'lik izgaradaki en kucuk esik. -> data/e_tau.json"""
import json, os, sys

KOK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(KOK, "deney"))
import karar as K  # noqa: E402

W, C, KA = K.yukle("pilot")
genel = [cid for cid, c in C.items() if c["truth"]["cell"] == "N_genel"]


def e_ozgu(cands, t):
    f = {x["eid"] for x in cands if x["f"] >= K.ALARM_F}
    return sum(1 for x in cands if x["e_rank"] <= K.E_TOP and x["e"] >= t and x["eid"] not in f)


secilen = None
izgara = []
for k in range(50, 100):
    t = k / 100
    m = sum(e_ozgu(KA[c], t) for c in genel) / len(genel)
    izgara.append((t, round(m, 4)))
    if secilen is None and m <= 0.10:
        secilen = t
json.dump({"e_tau": secilen, "kural": "min t (0.01 grid) with mean E-only alerts per general-population pilot customer <= 0.10",
           "izgara": izgara}, open(os.path.join(KOK, "data", "e_tau.json"), "w"), indent=1)
print("e_tau =", secilen, [x for x in izgara if abs(x[0] - secilen) < 0.035])
