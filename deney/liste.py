#!/usr/bin/env python3
"""Izleme listesi: UK Sanctions List (FCDO, OGL v3) + AB konsolide liste (FSF, Karar 2011/833/AB) -> data/watchlist.jsonl

Yalniz gercek kisiler ("Individual" / subjectType person) ve en az bir dogum tarihi olanlar alinir (on kayit, kapsam).
Her kayit: {eid, src, src_id, names:[{name, kind: primary|variation|alias_good|alias_low|nonlatin, script}],
            dobs:[{y, m, d, circa}], nats:[...], pob:[...], gender}
Iki listede ayni kisi: normalize ad + dogum tarihi ortaksa ayni kume (cluster) kimligi verilir.

Calistirma: ~/.venv/bin/python3 -I deney/liste.py
"""
import csv, json, os, re, sys, unicodedata
from lxml import etree

KOK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
HAM = os.path.join(KOK, "data", "raw")
sys.path.insert(0, os.path.join(KOK, "deney"))
from adlar import norm  # noqa: E402


def _script(s):
    for ch in s:
        if ch.isalpha() and ord(ch) > 0x024F:
            n = unicodedata.name(ch, "")
            for k in ("CYRILLIC", "ARABIC", "CJK", "HEBREW", "GEORGIAN", "KHMER", "THAI", "HANGUL", "ARMENIAN"):
                if k in n:
                    return k.lower()
            return "other"
    return "latin"


def _uk_dob(s):
    """'07/10/1952' -> {y,m,d}; 'dd/mm/1963' -> {y}; '--/--/1963' benzerleri."""
    m = re.match(r"^\s*(\d{2}|dd|--)/(\d{2}|mm|--)/(\d{4})\s*$", s or "")
    if not m:
        return None
    d, mo, y = m.groups()
    return {"y": int(y), "m": int(mo) if mo.isdigit() else None, "d": int(d) if d.isdigit() else None, "circa": False}


def uk():
    f = open(os.path.join(HAM, "UK-Sanctions-List.csv"), encoding="utf-8-sig")
    next(f)  # "Report Date: ..." satiri
    by = {}
    for x in csv.DictReader(f):
        if x["Designation Type"] != "Individual":
            continue
        by.setdefault(x["Unique ID"], []).append(x)
    out = []
    for uid, xs in by.items():
        names, dobs, nats, pob, gender = [], [], set(), set(), ""
        for x in xs:
            full = " ".join(p.strip() for p in [x["Name 1"], x["Name 2"], x["Name 3"], x["Name 4"], x["Name 5"], x["Name 6"]] if p.strip())
            nt = x["Name type"].strip().lower()
            st = x["Alias strength"].strip().lower()
            if full:
                kind = "primary" if nt == "primary name" else "variation" if nt == "primary name variation" else (
                    "alias_low" if st.startswith("low") else "alias_good")
                names.append({"name": full, "kind": kind, "script": _script(full)})
            nl = x["Name non-latin script"].strip()
            if nl:
                names.append({"name": nl, "kind": "nonlatin", "script": _script(nl)})
            dd = _uk_dob(x["D.O.B"])
            if dd and dd not in dobs:
                dobs.append(dd)
            for n in re.split(r"[,;]|\(\d+\)", x["Nationality(/ies)"] or ""):
                n = n.strip()
                if n:
                    nats.add(n.title())
            if x["Country of birth"].strip():
                pob.add(x["Country of birth"].strip().title())
            gender = gender or x["Gender"].strip()
        out.append({"src": "UK", "src_id": uid, "names": _tekil(names), "dobs": dobs, "nats": sorted(nats),
                    "pob": sorted(pob), "gender": gender})
    return out


def eu():
    ns = "{http://eu.europa.ec/fpi/fsd/export}"
    out = []
    for _, el in etree.iterparse(os.path.join(HAM, "EU-FSF-full.xml"), tag=ns + "sanctionEntity"):
        st = el.find(ns + "subjectType")
        if st is None or st.get("code") != "person":
            el.clear()
            continue
        names, dobs, nats, pob, gender = [], [], set(), set(), ""
        for i, na in enumerate(el.findall(ns + "nameAlias")):
            w = (na.get("wholeName") or "").strip()
            if not w:
                continue
            sc = _script(w)
            kind = "nonlatin" if sc != "latin" else ("primary" if i == 0 else "alias_good" if na.get("strong") == "true" else "alias_low")
            names.append({"name": w, "kind": kind, "script": sc})
            gender = gender or (na.get("gender") or "")
        for b in el.findall(ns + "birthdate"):
            y = b.get("year")
            full = b.get("birthdate")
            circa = b.get("circa") == "true"
            if full and re.match(r"^\d{4}-\d{2}-\d{2}$", full):
                dd = {"y": int(full[:4]), "m": int(full[5:7]), "d": int(full[8:10]), "circa": circa}
            elif y and y.isdigit():
                dd = {"y": int(y), "m": int(b.get("monthOfYear")) if (b.get("monthOfYear") or "").isdigit() else None,
                      "d": int(b.get("dayOfMonth")) if (b.get("dayOfMonth") or "").isdigit() else None, "circa": circa}
            else:
                dd = None
            if dd and dd not in dobs:
                dobs.append(dd)
            c = (b.get("countryDescription") or "").strip()
            if c and c != "UNKNOWN":
                pob.add(c.title())
        for c in el.findall(ns + "citizenship"):
            d = (c.get("countryDescription") or "").strip()
            if d and d != "UNKNOWN":
                nats.add(d.title())
        out.append({"src": "EU", "src_id": el.get("logicalId"), "names": _tekil(names), "dobs": dobs,
                    "nats": sorted(nats), "pob": sorted(pob), "gender": gender})
        el.clear()
    return out


def _tekil(names):
    seen, out = set(), []
    for n in names:
        k = n["name"].casefold()
        if k not in seen:
            seen.add(k)
            out.append(n)
    return out


def kumele(ents):
    """Iki listede ayni kisi: latin normalize adlardan biri + bir dogum yili+ay+gun (ya da yalniz yil) ortak."""
    anahtar = {}
    for e in ents:
        e["cluster"] = e["eid"]
    def kokler(e):
        return {(norm(n["name"]), d["y"], d.get("m"), d.get("d")) for n in e["names"] if n["script"] == "latin" for d in e["dobs"]}
    parent = {e["eid"]: e["eid"] for e in ents}
    def bul(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for e in ents:
        for k in kokler(e):
            if k in anahtar:
                a, b = bul(anahtar[k]), bul(e["eid"])
                if a != b:
                    parent[b] = a
            else:
                anahtar[k] = e["eid"]
    for e in ents:
        e["cluster"] = bul(e["eid"])


def main():
    ents = uk() + eu()
    tum = len(ents)
    ents = [e for e in ents if e["dobs"] and any(n["script"] == "latin" for n in e["names"])]
    for i, e in enumerate(ents):
        e["eid"] = f"W{i:05d}"
    kumele(ents)
    with open(os.path.join(KOK, "data", "watchlist.jsonl"), "w", encoding="utf-8") as f:
        for e in ents:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    from collections import Counter
    print("tum bireyler", tum, "-> DOB'lu ve latin adli", len(ents), Counter(e["src"] for e in ents))
    print("kume sayisi", len({e["cluster"] for e in ents}), "toplam ad", sum(len(e["names"]) for e in ents))
    print("ad turleri", Counter(n["kind"] for e in ents for n in e["names"]))
    print("yazi sistemleri", Counter(n["script"] for e in ents for n in e["names"]).most_common(6))


if __name__ == "__main__":
    main()
