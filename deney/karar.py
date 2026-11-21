#!/usr/bin/env python3
"""Alarm tanimi, dogru cevap (ground truth), kural tabanli kararlar ve LLM istemi.

Alarm (on kayit): F kanali token_set_ratio >= ALARM_F, musteri basina en yuksek ALARM_TOP kayit.
E kanali (gomme) ikincil hat: kosinus >= E_TAU ve E siralamasinda ilk E_TOP; E_TAU pilotta secilir, sonra dondurulur.

Dogru cevap (musteri duzeyi, birincil):
  pozitif musteri -> en az bir alarmi ESCALATE edilmeli (kaynak kisinin alarmi varsa)
  negatif musteri -> tum alarmlari DISCOUNT edilmeli; bunun icin her alarmda politikanin bir indirgeme kosulu
  (dogum tarihi cakismasi ya da N_yakin'da kayittaki hicbir ad parcasina benzemeyen soyadi) saglanmali; saglanmayan negatif
  musteri "belirsiz" sayilip analizden cikarilir (sayisi raporlanir).
"""
import json, os, sys

KOK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(KOK, "deney"))
from dob import durum, liste_dob_metni  # noqa: E402
from adlar import norm  # noqa: E402

ALARM_F = 85
ALARM_TOP = 5
E_TOP = 3
E_TAU = None  # pilot sonrasi on kayit ekine yazilir

POLITIKA = open(os.path.join(KOK, "deney", "politika.md"), encoding="utf-8").read().strip()


def yukle(set_):
    W = {}
    for l in open(os.path.join(KOK, "data", "watchlist.jsonl"), encoding="utf-8"):
        e = json.loads(l)
        W[e["eid"]] = e
    C = {}
    for l in open(os.path.join(KOK, "data", f"customers_{set_}.jsonl"), encoding="utf-8"):
        c = json.loads(l)
        C[c["cid"]] = c
    K = {}
    for l in open(os.path.join(KOK, "data", f"candidates_{set_}.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        K[r["cid"]] = r["cands"]
    return W, C, K


def alarmlar(cands, kanal="F", e_tau=None):
    f = [x for x in cands if x["f"] >= ALARM_F][:ALARM_TOP]
    if kanal == "F":
        return f
    tau = E_TAU if e_tau is None else e_tau
    e = [x for x in cands if x["e_rank"] <= E_TOP and x["e"] >= tau]
    ids = {x["eid"] for x in f}
    return f + [x for x in sorted(e, key=lambda x: -x["e"]) if x["eid"] not in ids]


def alarm_dogru(c, e):
    """Bir alarmin politika-dogru karari: 'escalate' | 'discount' | 'belirsiz'."""
    t = c["truth"]
    if t["label"] == "pos" and e["cluster"] == t["cluster"]:
        return "escalate"
    d = durum(c["dob"], e["dobs"])
    if d == "conflict":
        return "discount"
    if t.get("cell") == "N_yakin" and soyadi_farkli(t["new_surname"], e):
        return "discount"  # ad farkli (soyadi kaydin hicbir ad parcasina benzemiyor), DOB uyumlu
    if t["label"] == "pos":
        return "belirsiz"  # baska bir kayitla uyumlu DOB: ayni kisinin bagli olmayan kaydi olabilir
    return "belirsiz"


def soyadi_farkli(soyad, e):
    """Uretimdeki olcutun aynisi: kaydin her latin ad parcasina en az 3 harf ve iskelette en az 2 fark."""
    from rapidfuzz.distance import Levenshtein
    from musteri import iskelet
    s, ik = norm(soyad), iskelet(soyad)
    for n in e["names"]:
        if n["script"] != "latin":
            continue
        for tok in norm(n["name"]).split():
            if len(tok) >= 3 and (Levenshtein.distance(tok, s) < 3 or Levenshtein.distance(iskelet(tok), ik) < 2):
                return False
    return True


def musteri_dogru(c, als, W):
    """Musteri duzeyi dogru cevap: 'escalate' | 'discount' | 'belirsiz' | 'alarmsiz'."""
    if not als:
        return "alarmsiz"
    if c["truth"]["label"] == "pos":
        return "escalate" if any(W[a["eid"]]["cluster"] == c["truth"]["cluster"] for a in als) else "belirsiz"
    return "discount" if all(alarm_dogru(c, W[a["eid"]]) == "discount" for a in als) else "belirsiz"


# ---------------------------------------------------------------- kural tabanli kararlar

def kural_katı(c, e, a):
    """R1: ad alarmi + dogum tarihi tam uyum (kucuk farka tolerans yok)."""
    return "escalate" if durum(c["dob"], e["dobs"]) == "match" else "discount"


def kural_politika(c, e, a):
    """R2: politika madde 1'in tam uygulamasi; ad maddesi bulanik puanla (alarm esigi) temsil edilir."""
    if durum(c["dob"], e["dobs"]) == "conflict":
        return "discount"
    return "escalate" if a["f"] >= ALARM_F else "discount"


KURALLAR = {"R0_hepsi": lambda c, e, a: "escalate", "R1_kati": kural_katı, "R2_politika": kural_politika}


# ---------------------------------------------------------------- LLM istemi

SISTEM = POLITIKA + """

Reply with a single JSON object and nothing else:
{"name_assessment": "same" | "variant" | "different",
 "dob_assessment": "match" | "minor_discrepancy" | "conflict",
 "decision": "ESCALATE" | "DISCOUNT",
 "reason": "<one or two sentences citing the evidence>"}"""


def kayit_metni(e):
    adlar = []
    for n in e["names"]:
        tur = {"primary": "primary name", "variation": "name variation", "alias_good": "alias (good quality)",
               "alias_low": "alias (low quality)", "nonlatin": f"name in {n['script']} script"}[n["kind"]]
        adlar.append(f"  - {n['name']} [{tur}]")
    s = "List entry:\n" + "\n".join(adlar[:25])
    s += "\nDate(s) of birth on list: " + "; ".join(liste_dob_metni(d) for d in e["dobs"])
    if e["nats"]:
        s += "\nNationality on list: " + "; ".join(e["nats"])
    if e["pob"]:
        s += "\nCountry of birth on list: " + "; ".join(e["pob"])
    return s


def istem(c, e):
    kul = (f"Customer record:\n  Name: {c['name']}\n  Date of birth: {c['dob']}\n  Nationality: {c['nationality']}\n\n"
           + kayit_metni(e) + "\n\nApply the policy and return the JSON object.")
    return [{"role": "system", "content": SISTEM}, {"role": "user", "content": kul}]
