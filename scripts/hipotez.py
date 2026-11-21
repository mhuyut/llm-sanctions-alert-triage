#!/usr/bin/env python3
"""On kayitli hipotez testleri (H1-H6): data/runs/full/*.jsonl -> data/hipotez_full.json

  ~/.venv/bin/python3 -I scripts/hipotez.py [full]
Analiz plani (makale/hipotezler_onkayit.md): Wilson araliklari, exact McNemar, Holm (her hipotezde LLM'ler arasi).
Ayristirilamayan kararlar 'escalate' sayilir. H1 icin tek yonlu p, Newcombe (1998, yontem 10) eslesmis farkin
ust sinirinin 2 puana esit oldugu guven duzeyinden bulunur; on kayittaki %95 iki yonlu aralik = tek yonlu 0,025.
"""
import json, math, os, sys
from collections import defaultdict

from scipy.stats import binomtest, fisher_exact, norm

KOK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(KOK, "deney"))
import karar as K  # noqa: E402
from dob import durum  # noqa: E402

SET = sys.argv[1] if len(sys.argv) > 1 else "full"
LLM = ["deepseek-v4.1-flash", "qwen3.8-flash-next", "gemma-4-31b"]  # degisiklik 2: glm-5.3 cikarildi
ALFA = 0.05
NI_MARJ = 0.02
DOB_AD = {"match": "match", "minor": "minor_discrepancy", "conflict": "conflict"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def newcombe(x, y, z=1.96):
    """Eslesmis iki oranin farki p1-p2 (x, y: 0/1 listeleri), Newcombe yontem 10."""
    n = len(x)
    a = sum(1 for i, j in zip(x, y) if i and j)
    b = sum(1 for i, j in zip(x, y) if i and not j)
    c = sum(1 for i, j in zip(x, y) if not i and j)
    d = n - a - b - c
    p1, l1, u1 = wilson(a + b, n, z)
    p2, l2, u2 = wilson(a + c, n, z)
    den = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    phi = (a * d - b * c) / den if den else 0.0
    dl = math.sqrt(max(0.0, (p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2))
    du = math.sqrt(max(0.0, (u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2))
    return p1 - p2, p1 - p2 - dl, p1 - p2 + du, {"a": a, "b": b, "c": c, "d": d}


def ni_p(x, y, marj):
    """H0: p1-p2 >= marj icin tek yonlu p: ust sinirin marj'a esit oldugu tek yonlu alfa (ikiye bolme)."""
    if newcombe(x, y)[0] >= marj:
        return 1.0
    lo, hi = 0.0, 40.0  # ust sinir z ile artar; ust(z*) = marj
    for _ in range(80):
        z = (lo + hi) / 2
        if newcombe(x, y, z)[2] < marj:
            lo = z
        else:
            hi = z
    return float(norm.sf(lo))


def mcnemar_tek(b, c):
    """Exact McNemar, tek yonlu: H1 = b > c (b: yalniz birinci olayda, c: yalniz ikincide)."""
    if b + c == 0:
        return 1.0
    return float(binomtest(b, b + c, 0.5, alternative="greater").pvalue)


def holm(ps):
    ad = sorted(ps, key=lambda k: ps[k])
    m, out, onceki = len(ad), {}, 0.0
    for i, k in enumerate(ad):
        onceki = max(onceki, min(1.0, (m - i) * ps[k]))
        out[k] = onceki
    return out


def r(x, k=4):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(x, k)


def main():
    W, C, KA = K.yukle(SET)
    # Kurulum hatasi (05.11.2026, sonuclardan sonra bulundu): dob_kucuk gun hanesini degistirince gun 0 ya da >28 cikarsa
    # 18 yaziyor; bu musterilerin tarihi kendi kaydiyla politikaya gore 'conflict'. Onkayitli analiz degismez;
    # bu musteriler dislanarak H1, H4, H5 ayrica (post hoc duyarlilik) raporlanir.
    kusurlu = {cid for cid, c in C.items() if c["truth"]["label"] == "pos" and durum(c["dob"], W[c["truth"]["eid"]]["dobs"]) == "conflict"}
    tau = json.load(open(os.path.join(KOK, "data", "e_tau.json")))["e_tau"]
    runs = {}
    for m in LLM:
        d = {}
        for l in open(os.path.join(KOK, "data", "runs", SET, f"{m}.jsonl"), encoding="utf-8"):
            x = json.loads(l)
            if not x.get("error") or x["tid"] not in d:
                d[x["tid"]] = x
        runs[m] = d
    al = {"F": {cid: K.alarmlar(KA[cid], "F") for cid in C}, "FE": {cid: K.alarmlar(KA[cid], "FE", e_tau=tau) for cid in C}}
    truth = {p: {cid: K.musteri_dogru(C[cid], al[p][cid], W) for cid in C} for p in al}

    def dec(n, cid, a):
        if n == "R2":
            return K.KURALLAR["R2_politika"](C[cid], W[a["eid"]], a)
        x = runs[n].get(f"{cid}|{a['eid']}")
        return x["decision"] if x and x.get("decision") else "escalate"

    def esc(n, p, cid):
        return any(dec(n, cid, a) == "escalate" for a in al[p][cid])

    out = {"set": SET, "models": LLM, "alpha": ALFA, "ni_margin": NI_MARJ, "n_dob_construction_error": len(kusurlu)}
    out.update(testler(C, W, al, truth, esc, runs, set()))
    out["sensitivity_excl_dob_construction_error"] = {h: v for h, v in testler(C, W, al, truth, esc, runs, kusurlu).items()
                                                      if h in ("H1", "H4", "H5")}
    json.dump(out, open(os.path.join(KOK, "data", f"hipotez_{SET}.json"), "w"), indent=1, ensure_ascii=False)
    for etiket, blok in (("onkayitli", out), ("duyarlilik (kurulum hatasi dislandi)", out["sensitivity_excl_dob_construction_error"])):
        print("====", etiket)
        for h in ("H1", "H2", "H3", "H4", "H5", "H6"):
            if h not in blok:
                continue
            print(h)
            for k, v in blok[h].items():
                print("  ", k, {x: y for x, y in v.items() if x != "table"})


def testler(C, W, al, truth, esc, runs, haric):
    def kume(p, t):
        return sorted(cid for cid in C if truth[p][cid] == t and cid not in haric)

    out = {}

    # H1: F hatti, kacirma orani LLM - R2 < 2 puan (eslesmis Newcombe)
    pos = kume("F", "escalate")
    ry = [not esc("R2", "F", cid) for cid in pos]
    h1, p1 = {}, {}
    for m in LLM:
        mx = [not esc(m, "F", cid) for cid in pos]
        fark, lo, hi, tab = newcombe(mx, ry)
        p1[m] = ni_p(mx, ry, NI_MARJ)
        h1[m] = {"n": len(pos), "miss_llm": r(sum(mx) / len(pos)), "miss_r2": r(sum(ry) / len(pos)),
                 "diff": r(fark), "ci95": [r(lo), r(hi)], "table": tab, "p_one_sided": r(p1[m], 6)}
    for m, ph in holm(p1).items():
        h1[m]["p_holm"] = r(ph, 6)
        h1[m]["supported"] = ph < ALFA / 2 and h1[m]["ci95"][1] < NI_MARJ
    out["H1"] = h1

    # H2: F hatti, alarmli negatiflerde LLM R2'den az yukseltir (exact McNemar tek yonlu)
    neg = kume("F", "discount")
    h2, p2 = {}, {}
    for m in LLM:
        b = sum(1 for cid in neg if esc("R2", "F", cid) and not esc(m, "F", cid))
        c = sum(1 for cid in neg if esc(m, "F", cid) and not esc("R2", "F", cid))
        p2[m] = mcnemar_tek(b, c)
        h2[m] = {"n": len(neg), "esc_llm": sum(esc(m, "F", cid) for cid in neg), "esc_r2": sum(esc("R2", "F", cid) for cid in neg),
                 "only_r2": b, "only_llm": c, "p_one_sided": p2[m]}
    for m, ph in holm(p2).items():
        h2[m]["p_holm"] = ph
        h2[m]["supported"] = ph < ALFA
    out["H2"] = h2

    # H3: F recall transliterasyon kosullarinda tam addan dusuk (Fisher tek yonlu); E kanali ekleyince artar (McNemar)
    def hit(p, cid):
        return any(W[a["eid"]]["cluster"] == C[cid]["truth"]["cluster"] for a in al[p][cid])

    def kosul(ad):
        return [cid for cid, c in C.items() if c["truth"]["label"] == "pos" and c["truth"]["cell"].split("|")[0] == ad and cid not in haric]

    ex = kosul("P_exact")
    ex_hit = sum(hit("F", cid) for cid in ex)
    h3, p3 = {}, {}
    for ad in ("P_tr_arap", "P_kiril_tr"):
        cs = kosul(ad)
        fh = sum(hit("F", cid) for cid in cs)
        _, pf = fisher_exact([[ex_hit, len(ex) - ex_hit], [fh, len(cs) - fh]], alternative="greater")
        yalniz_fe = sum(1 for cid in cs if hit("FE", cid) and not hit("F", cid))
        yalniz_f = sum(1 for cid in cs if hit("F", cid) and not hit("FE", cid))
        pm = mcnemar_tek(yalniz_fe, yalniz_f)
        p3[ad + "|lower"], p3[ad + "|E"] = float(pf), pm
        h3[ad] = {"n": len(cs), "recall_F": r(fh / len(cs)), "recall_FE": r(sum(hit("FE", cid) for cid in cs) / len(cs)),
                  "recall_F_exact": r(ex_hit / len(ex)), "n_exact": len(ex), "p_lower_fisher": float(pf),
                  "only_FE": yalniz_fe, "only_F": yalniz_f, "p_E_mcnemar": pm}
    hp = holm(p3)
    for ad in h3:
        h3[ad]["p_holm_lower"], h3[ad]["p_holm_E"] = hp[ad + "|lower"], hp[ad + "|E"]
        h3[ad]["supported"] = hp[ad + "|lower"] < ALFA and hp[ad + "|E"] < ALFA
    out["H3"] = h3

    # H4: FE hatti, pozitiflerde LLM R2'den fazla yukseltir (exact McNemar tek yonlu)
    posfe = kume("FE", "escalate")
    h4, p4 = {}, {}
    for m in LLM:
        b = sum(1 for cid in posfe if esc(m, "FE", cid) and not esc("R2", "FE", cid))
        c = sum(1 for cid in posfe if esc("R2", "FE", cid) and not esc(m, "FE", cid))
        p4[m] = mcnemar_tek(b, c)
        h4[m] = {"n": len(posfe), "esc_llm": sum(esc(m, "FE", cid) for cid in posfe), "esc_r2": sum(esc("R2", "FE", cid) for cid in posfe),
                 "only_llm": b, "only_r2": c, "p_one_sided": p4[m]}
    for m, ph in holm(p4).items():
        h4[m]["p_holm"] = ph
        h4[m]["supported"] = ph < ALFA
    out["H4"] = h4

    # H5: F hatti, kacirma D_kucuk > D_ayni (Fisher tek yonlu)
    h5, p5 = {}, {}
    for m in LLM:
        t = defaultdict(lambda: [0, 0])
        for cid in pos:
            k = C[cid]["truth"]["cell"].split("|")[1]
            t[k][0] += not esc(m, "F", cid)
            t[k][1] += 1
        ku, ay = t["D_kucuk"], t["D_ayni"]
        _, pf = fisher_exact([[ku[0], ku[1] - ku[0]], [ay[0], ay[1] - ay[0]]], alternative="greater")
        p5[m] = float(pf)
        h5[m] = {"miss_D_kucuk": [ku[0], ku[1]], "miss_D_ayni": [ay[0], ay[1]], "p_one_sided": float(pf)}
    for m, ph in holm(p5).items():
        h5[m]["p_holm"] = ph
        h5[m]["supported"] = ph < ALFA
    out["H5"] = h5

    # H6: dob_assessment dogrulugu > 0,95 (tek yonlu exact binom; FE hattindaki tum ayristirilmis alarmlar)
    h6, p6 = {}, {}
    gorev = [(cid, a) for cid in C for a in al["FE"][cid]]
    for m in LLM:
        k = n = 0
        for cid, a in gorev:
            x = runs[m].get(f"{cid}|{a['eid']}")
            if not x or not x.get("parsed"):
                continue
            n += 1
            k += x.get("dob_assessment") == DOB_AD[durum(C[cid]["dob"], W[a["eid"]]["dobs"])]
        bt = binomtest(k, n, 0.95, alternative="greater")
        p6[m] = float(bt.pvalue)
        h6[m] = {"k": k, "n": n, "acc": r(k / n), "lower95_one_sided": r(bt.proportion_ci(0.95).low), "p_one_sided": p6[m]}
    for m, ph in holm(p6).items():
        h6[m]["p_holm"] = ph
        h6[m]["supported"] = ph < ALFA
    out["H6"] = h6

    return out


if __name__ == "__main__":
    main()
