#!/usr/bin/env python3
"""Analiz: data/runs/<set>/*.jsonl + aday/musteri dosyalari -> data/stats_<set>.json

  ~/.venv/bin/python3 -I scripts/analiz.py pilot
Ayristirilamayan ya da eksik LLM kararlari 'escalate' sayilir (on kayit); duyarlilik icin 'discount' hali de raporlanir.
"""
import glob, json, math, os, statistics, sys
from collections import Counter, defaultdict

KOK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(KOK, "deney"))
import karar as K  # noqa: E402
from dob import durum  # noqa: E402

SET = sys.argv[1] if len(sys.argv) > 1 else "pilot"
DOB_AD = {"match": "match", "minor": "minor_discrepancy", "conflict": "conflict"}


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(p, 4), round(max(0, c - h), 4), round(min(1, c + h), 4)]


def main():
    W, C, KA = K.yukle(SET)
    tau = json.load(open(os.path.join(KOK, "data", "e_tau.json")))["e_tau"]
    runs = {}
    for fp in sorted(glob.glob(os.path.join(KOK, "data", "runs", SET, "*.jsonl"))):
        d = {}
        for l in open(fp, encoding="utf-8"):
            r = json.loads(l)
            if not r.get("error") or r["tid"] not in d:
                d[r["tid"]] = r
        runs[d[next(iter(d))]["model"] if d else os.path.basename(fp)] = d
    st = {"set": SET, "e_tau": tau, "n_customers": len(C), "cells": dict(Counter(c["truth"]["cell"] for c in C.values()))}

    # ---- 1. asama
    al = {"F": {cid: K.alarmlar(KA[cid], "F") for cid in C}, "FE": {cid: K.alarmlar(KA[cid], "FE", e_tau=tau) for cid in C}}
    rec = defaultdict(dict)
    for p in ("F", "FE"):
        by = defaultdict(lambda: [0, 0])
        for cid, c in C.items():
            if c["truth"]["label"] != "pos":
                continue
            hit = any(W[a["eid"]]["cluster"] == c["truth"]["cluster"] for a in al[p][cid])
            for key in (c["truth"]["cell"], c["truth"]["cell"].split("|")[0], "ALL"):
                by[key][0] += hit
                by[key][1] += 1
        rec[p] = {k: {"hit": v[0], "n": v[1], "rate": wilson(*v)} for k, v in sorted(by.items())}
        st[f"alerts_{p}"] = sum(len(v) for v in al[p].values())
        st[f"alerts_per_customer_{p}"] = round(st[f"alerts_{p}"] / len(C), 4)
    st["stage1_recall"] = rec

    # ---- dogru cevap
    truth = {p: {cid: K.musteri_dogru(C[cid], al[p][cid], W) for cid in C} for p in al}
    st["truth_counts"] = {p: dict(Counter(truth[p].values())) for p in truth}

    # ---- karar vericiler
    def karar_kural(fn, c, a):
        return fn(c, W[a["eid"]], a)

    def karar_llm(m, cid, a, eksik="escalate"):
        r = runs[m].get(f"{cid}|{a['eid']}")
        if not r or not r.get("decision"):
            return eksik
        return r["decision"]

    karar = {n: (lambda fn: (lambda cid, a: karar_kural(fn, C[cid], a)))(fn) for n, fn in K.KURALLAR.items()}
    tum = {f"{cid}|{a['eid']}" for cid in C for a in al["FE"][cid]}
    for m in runs:
        if not tum <= set(runs[m]):
            continue  # alt orneklemle kosan model (pilotta glm-5.3): musteri duzeyi karar hesaplanmaz
        karar[m] = (lambda m: (lambda cid, a: karar_llm(m, cid, a)))(m)
        karar[m + "|eksik=discount"] = (lambda m: (lambda cid, a: karar_llm(m, cid, a, "discount")))(m)

    res = {}
    for p in al:
        res[p] = {}
        for n, f in karar.items():
            miss, npos, fp, nneg, esc_neg = 0, 0, 0, 0, 0
            cell = defaultdict(lambda: [0, 0])
            for cid, c in C.items():
                t = truth[p][cid]
                if t not in ("escalate", "discount"):
                    continue
                esc = any(f(cid, a) == "escalate" for a in al[p][cid])
                key = c["truth"]["cell"]
                if t == "escalate":
                    npos += 1
                    miss += not esc
                    cell[key][0] += not esc
                else:
                    nneg += 1
                    fp += esc
                    cell[key][0] += esc
                cell[key][1] += 1
            res[p][n] = {"miss": wilson(miss, npos), "n_pos": npos, "fp_rate": wilson(fp, nneg), "n_neg": nneg,
                         "escalated_neg": fp, "workload_per_1000": round(1000 * fp / len(C), 2),
                         "cells": {k: v for k, v in sorted(cell.items())}}
    st["disposition"] = res

    # ---- LLM gorev istatistikleri, gerekce dogrulugu, tutarlilik
    tasks = {f"{cid}|{a['eid']}": (cid, a) for cid in C for a in al["FE"][cid]}
    llm = {}
    for m, d in runs.items():
        mt = [t for t in tasks if t in d] if not set(tasks) <= set(d) else list(tasks)
        n = len(mt) if len(mt) < len(tasks) else len(tasks)
        got = [d.get(t) for t in (mt if len(mt) < len(tasks) else tasks)]
        ok = [r for r in got if r and r.get("parsed")]
        lat = [r["latency_s"] for r in got if r and r.get("latency_s")]
        dob_ok, dob_n, ad_ok, ad_n, tut_ok, tut_n = 0, 0, 0, 0, 0, 0
        for tid, (cid, a) in tasks.items():
            r = d.get(tid)
            if not r or not r.get("parsed"):
                continue
            c, e = C[cid], W[a["eid"]]
            gercek = DOB_AD[durum(c["dob"], e["dobs"])]
            dob_n += 1
            dob_ok += r.get("dob_assessment") == gercek
            t = c["truth"]
            if t.get("eid") == a["eid"]:
                ad_n += 1
                beklenen = {"different"} if t["cell"] == "N_yakin" else {"same", "variant"}
                ad_ok += r.get("name_assessment") in beklenen
            if r.get("dob_assessment") in ("match", "minor_discrepancy", "conflict") and r.get("name_assessment") in ("same", "variant", "different"):
                tut_n += 1
                beklenen_k = "discount" if (r["dob_assessment"] == "conflict" or r["name_assessment"] == "different") else "escalate"
                tut_ok += r["decision"] == beklenen_k
        llm[m] = {"tasks": n, "answered": sum(1 for r in got if r and not r.get("error")), "parsed": len(ok),
                  "parse_rate": wilson(len(ok), n), "latency_median_s": round(statistics.median(lat), 2) if lat else None,
                  "in_tok_mean": round(statistics.mean([r["in_tok"] for r in ok if r.get("in_tok")]), 1) if ok else None,
                  "out_tok_mean": round(statistics.mean([r["out_tok"] for r in ok if r.get("out_tok")]), 1) if ok else None,
                  "tok_total": sum((r.get("in_tok") or 0) + (r.get("out_tok") or 0) for r in ok),
                  "dob_accuracy": wilson(dob_ok, dob_n), "name_accuracy_own_entry": wilson(ad_ok, ad_n),
                  "decision_consistency": wilson(tut_ok, tut_n),
                  "served": dict(Counter(r.get("served_model") for r in ok))}
    st["llm"] = llm
    if "gemma-4-31b" in runs and "gemma4:31b" in runs:
        a_, b_ = runs["gemma-4-31b"], runs["gemma4:31b"]
        ort = [t for t in tasks if a_.get(t, {}).get("decision") and b_.get(t, {}).get("decision")]
        ayni = sum(a_[t]["decision"] == b_[t]["decision"] for t in ort)
        st["H7_gemma_agreement"] = {"n": len(ort), "agree": wilson(ayni, len(ort))}

    # ---- kredi (usage.jsonl): pilot boyunca hesap bazinda ilk/son kredi
    up = os.path.join(KOK, "logs", "usage.jsonl")
    if os.path.exists(up):
        kr = defaultdict(list)
        tok = defaultdict(int)
        for l in open(up):
            u = json.loads(l)
            if u.get("kredi") is not None:
                kr[u["acct"]].append(float(u["kredi"]))
            tok[u["acct"]] += u.get("total") or 0
        st["evren_credit"] = {str(k): {"first": v[0], "last": v[-1], "spent": round(v[0] - v[-1], 4), "tokens": tok[k]}
                              for k, v in kr.items()}
    json.dump(st, open(os.path.join(KOK, "data", f"stats_{SET}.json"), "w"), indent=1, ensure_ascii=False)

    # ---- ozet
    print(f"[{SET}] musteri {len(C)}  alarm F {st['alerts_F']}  FE {st['alerts_FE']}  tau {tau}")
    print("dogru cevap:", st["truth_counts"])
    print("1. asama recall:", {p: {k: v["rate"][0] for k, v in rec[p].items() if "|" not in k} for p in rec})
    for p in res:
        print(f"--- hat {p}")
        for n, v in res[p].items():
            if "eksik=" in n:
                continue
            print(f"  {n:22s} miss {v['miss'][0]} (n={v['n_pos']})  FP {v['fp_rate'][0]} (n={v['n_neg']})  yuk/1000 {v['workload_per_1000']}")
    for m, v in llm.items():
        print(f"  {m:22s} parse {v['parse_rate'][0]}  lat {v['latency_median_s']}  dobacc {v['dob_accuracy'][0]}  adacc {v['name_accuracy_own_entry'][0]}  tutarli {v['decision_consistency'][0]}  tok {v['tok_total']}")
    if "evren_credit" in st:
        print("kredi:", st["evren_credit"])


if __name__ == "__main__":
    main()
