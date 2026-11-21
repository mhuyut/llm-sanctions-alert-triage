#!/usr/bin/env python3
"""Sentetik musteri tabani: data/customers_<set>.jsonl

Hucreler (on kayit):
  Pozitif (listedeki kisinin kendisi) = ad varyanti (6) x dogum tarihi (2)
    ad:  P_exact (birincil ad), P_alias (iyi kaliteli takma ad), P_tr_arap (Arapca kokenli adin Turkce imlasi),
         P_kiril_tr (Kiril adin Turkce romanizasyonu), P_sira (ad sirasi / orta ad dusmesi), P_hata (yazim hatasi + Turkce buyuk harf)
    dob: D_ayni (liste tarihiyle uyumlu), D_kucuk (politikadaki kucuk fark: gun-ay yer degisimi, +-1 yil, tek hane)
  Negatif:
    N_adas  = ayni ad donusumleri (6), dogum tarihi en az 5 yil farkli (cakisma)  -> farkli kisi
    N_yakin = soyadi (ya da ilk ad) baska, en az 3 harf farkli bir adla degistirilmis, dogum tarihi ayni -> farkli kisi
    N_genel = genel nufus: Turk adlari + liste adlarindan rastgele yeniden birlestirilmis adlar, rastgele dogum tarihi
Pilot ve tam kume farkli kumelerden (cluster) cekilir; ayni kisi iki kumede kullanilmaz.

Calistirma: ~/.venv/bin/python3 -I deney/musteri.py --set pilot|full
"""
import argparse, json, os, random, sys

KOK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(KOK, "deney"))
from adlar import norm, tr_arap, kiril_tr, sira_kismi, yazim_hatasi, _cap  # noqa: E402
from rapidfuzz.distance import Levenshtein  # noqa: E402
from rapidfuzz import fuzz  # noqa: E402

BOYUT = {"pilot": {"pos": 10, "adas": 10, "yakin": 40, "genel": 2000},
         "full": {"pos": 100, "adas": 100, "yakin": 400, "genel": 10000}}
PILOT_PAY = 0.12  # kumelerin bu kadari pilota ayrilir
TOHUM = 20261104

ARAP_ULKE = {"Afghanistan", "Iran", "Iraq", "Syria", "Syrian Arab Republic", "Lebanon", "Yemen", "Saudi Arabia", "Libya",
             "Egypt", "Sudan", "Somalia", "Pakistan", "Jordan", "Kuwait", "Qatar", "United Arab Emirates", "Bahrain",
             "Oman", "Tunisia", "Algeria", "Morocco", "Mali", "Palestine", "Mauritania", "Niger", "Chad",
             "Iran (Islamic Republic Of)", "Libyan Arab Jamahiriya", "Palestinian"}
TR_AD = ("Mehmet Ahmet Mustafa Ali Hüseyin Hasan İbrahim Murat Ömer Yusuf Emre Burak Can Kemal Osman Halil Süleyman "
         "Recep Serkan Hakan Fatih Gökhan Selim Cem Kerem Eren Enes Furkan Berk Arda Kaan Yasin Oğuz Tolga Volkan Onur "
         "Ayşe Fatma Emine Hatice Zeynep Elif Meryem Şerife Zehra Hülya Esra Merve Büşra Kübra Seda Derya Özlem Aslı "
         "Ebru Gamze Tuğba Sevgi Nur Hacer Songül Hanife Melek Dilek Gül Leyla Sibel Pınar Ece Defne Yağmur").split()
TR_SOYAD = ("Yılmaz Kaya Demir Şahin Çelik Yıldız Yıldırım Öztürk Aydın Özdemir Arslan Doğan Kılıç Aslan Çetin Kara Koç "
            "Kurt Özkan Şimşek Polat Özcan Korkmaz Çakır Erdoğan Yavuz Can Acar Şen Aktaş Güler Yalçın Güneş Bozkurt "
            "Bulut Keskin Ünal Turan Gül Özer Işık Kaplan Avcı Sarı Tekin Taş Köse Yüksel Ateş Aktürk Karaca Uçar "
            "Kocaman Duman Bayram Erdem Ekinci Soylu Tunç Akın Uysal Coşkun Sezer Altun Kahraman Karakaya Eren Akbulut").split()


def yukle():
    with open(os.path.join(KOK, "data", "watchlist.jsonl"), encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def ad_listesi(e, kinds):
    return [n["name"] for n in e["names"] if n["kind"] in kinds and n["script"] == "latin"]


def birincil(e):
    a = ad_listesi(e, ("primary",)) or ad_listesi(e, ("variation", "alias_good")) or ad_listesi(e, ("alias_low",))
    return a[0]


def arap_mi(e):
    return any(n["script"] == "arabic" for n in e["names"]) or any(x in ARAP_ULKE for x in e["nats"] + e["pob"])


def varyant(e, tur, rng):
    """Ad donusumu; uygun degilse None."""
    p = birincil(e)
    if tur == "exact":
        return p
    if tur == "alias":
        al = [a for a in ad_listesi(e, ("alias_good", "variation")) if norm(a) != norm(p)]
        return rng.choice(al) if al else None
    if tur == "tr_arap":
        if not arap_mi(e):
            return None
        for a in [p] + ad_listesi(e, ("variation", "alias_good")):
            v = tr_arap(a, rng)
            if v and len(v.split()) >= 2:
                return v
        return None
    if tur == "kiril_tr":
        cy = [n["name"] for n in e["names"] if n["script"] == "cyrillic"]
        return kiril_tr(rng.choice(cy)) if cy else None
    if tur == "sira":
        return sira_kismi(p, rng)
    if tur == "hata":
        return yazim_hatasi(p, rng)
    raise ValueError(tur)


def tam_tarih(l, rng):
    y = l["y"]
    m = l.get("m") or rng.randint(1, 12)
    d = l.get("d") or rng.randint(1, 28)
    return y, m, d


def dob_ayni(e, rng):
    y, m, d = tam_tarih(rng.choice(e["dobs"]), rng)
    return f"{y:04d}-{m:02d}-{d:02d}"


def dob_kucuk(e, rng):
    l = rng.choice(e["dobs"])
    y, m, d = tam_tarih(l, rng)
    if l.get("m") is None or l.get("d") is None:
        y += rng.choice([-1, 1])
    else:
        sec = ["yil"] + (["yer"] if d <= 12 and d != m else []) + (["hane"] if d >= 10 else [])
        k = rng.choice(sec)
        if k == "yil":
            y += rng.choice([-1, 1])
        elif k == "yer":
            m, d = d, m
        else:  # gunun birler hanesi
            d = (d // 10) * 10 + ((d % 10 + rng.choice([1, 2, 3])) % 10)
            if d == 0 or d > 28:
                d = 18
    return f"{y:04d}-{m:02d}-{d:02d}"


def dob_cakisma(e, rng, fark=5):
    yillar = [l["y"] for l in e["dobs"]]
    for _ in range(100):
        y = rng.randint(1940, 2006)
        if all(abs(y - z) >= fark for z in yillar):
            return f"{y:04d}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"
    return None


def uyruk(e, rng, p_liste):
    if (e["nats"] or e["pob"]) and rng.random() < p_liste:
        return rng.choice(e["nats"] or e["pob"])
    return "Turkey"


def iskelet(t):
    """Kaba sessiz harf iskeleti: harf cevirisi farklarini (kh/h, j/y, w/v, ou/u, sesliler) yok sayar."""
    t = norm(t).replace(" ", "")
    for a, b in (("kh", "h"), ("sh", "s"), ("ch", "c"), ("ph", "f"), ("tz", "c"), ("ts", "c"), ("dj", "c"),
                 ("j", "y"), ("w", "v"), ("q", "k"), ("ck", "k"), ("x", "ks"), ("z", "s")):
        t = t.replace(a, b)
    t = "".join(ch for ch in t if ch not in "aeiouyh")
    out = []
    for ch in t:
        if not out or out[-1] != ch:
            out.append(ch)
    return "".join(out)


def yakin_ad(e, soyadlar, rng):
    """Yalniz soyadini (son parca) gorunuste benzer ama farkli bir soyadiyla degistir: en az 3 harf farki ve
    sessiz harf iskeleti en az 2 farkli (harf cevirisi varyanti olmasin); kisinin hicbir adinda gecmesin."""
    toks = birincil(e).split()
    if len(toks) < 2:
        return None
    t = norm(toks[-1])
    if len(t) < 4 or t.startswith(("al ", "el ")):
        return None
    kendi = {norm(x) for n in e["names"] if n["script"] == "latin" for x in n["name"].split()}
    ik = iskelet(t)
    aday = [s for s in soyadlar if s[:1].lower() == t[:1] and norm(s) not in kendi
            and Levenshtein.distance(norm(s), t) >= 3 and fuzz.ratio(norm(s), t) >= 55
            and Levenshtein.distance(iskelet(s), ik) >= 2]
    if not aday:
        return None
    yeni = rng.choice(aday)
    return " ".join(toks[:-1] + [yeni]), yeni


ADLAR = ["exact", "alias", "tr_arap", "kiril_tr", "sira", "hata"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=["pilot", "full"], required=True)
    a = ap.parse_args()
    W = yukle()
    kumeler = sorted({e["cluster"] for e in W})
    random.Random(TOHUM).shuffle(kumeler)
    k_pilot = set(kumeler[: int(len(kumeler) * PILOT_PAY)])
    havuz = [e for e in W if (e["cluster"] in k_pilot) == (a.set == "pilot")]
    rng = random.Random(TOHUM + (1 if a.set == "pilot" else 2))
    rng.shuffle(havuz)
    B = BOYUT[a.set]
    kullanilan = set()
    out = []

    def al(tur, n, yap):
        sayi = 0
        for e in havuz:
            if sayi >= n:
                break
            if e["cluster"] in kullanilan:
                continue
            r = yap(e)
            if r is None:
                continue
            kullanilan.add(e["cluster"])
            out.append(r)
            sayi += 1
        if sayi < n:
            print(f"UYARI {tur}: {sayi}/{n}", flush=True)

    for tur in ADLAR:
        for dk in ("D_ayni", "D_kucuk"):
            def yap(e, tur=tur, dk=dk):
                ad = varyant(e, tur, rng)
                if not ad:
                    return None
                dob = dob_ayni(e, rng) if dk == "D_ayni" else dob_kucuk(e, rng)
                return {"name": ad, "dob": dob, "nationality": uyruk(e, rng, 0.8),
                        "truth": {"label": "pos", "cell": f"P_{tur}|{dk}", "eid": e["eid"], "cluster": e["cluster"]}}
            al(f"P_{tur}|{dk}", B["pos"], yap)
    for tur in ADLAR:
        def yap(e, tur=tur):
            ad = varyant(e, tur, rng)
            dob = dob_cakisma(e, rng) if ad else None
            if not dob:
                return None
            return {"name": ad, "dob": dob, "nationality": uyruk(e, rng, 0.5),
                    "truth": {"label": "neg", "cell": f"N_adas_{tur}", "eid": e["eid"], "cluster": e["cluster"]}}
        al(f"N_adas_{tur}", B["adas"], yap)
    soyadlar = sorted({t for e in W for n in e["names"] if n["kind"] == "primary" and n["script"] == "latin"
                       for t in [n["name"].split()[-1]] if len(t) >= 4})
    def yap_y(e):
        r = yakin_ad(e, soyadlar, rng)
        if not r:
            return None
        ad, yeni = r
        return {"name": ad, "dob": dob_ayni(e, rng), "nationality": uyruk(e, rng, 0.5),
                "truth": {"label": "neg", "cell": "N_yakin", "eid": e["eid"], "cluster": e["cluster"], "new_surname": yeni}}
    al("N_yakin", B["yakin"], yap_y)
    # genel nufus: %70 Turk adi, %30 liste ad parcalarindan yeniden birlestirme
    ilk = [n["name"].split()[0] for e in havuz for n in e["names"] if n["kind"] == "primary" and n["script"] == "latin"
           and len(n["name"].split()) >= 2]
    son = [n["name"].split()[-1] for e in havuz for n in e["names"] if n["kind"] == "primary" and n["script"] == "latin"
           and len(n["name"].split()) >= 2]
    for _ in range(B["genel"]):
        if rng.random() < 0.7:
            ad = f"{rng.choice(TR_AD)} {rng.choice(TR_SOYAD)}"
            if rng.random() < 0.15:
                ad = f"{rng.choice(TR_AD)} {ad}"
            uy = "Turkey"
        else:
            ad = f"{_cap(rng.choice(ilk).lower())} {rng.choice(son)}"
            uy = rng.choice(["Turkey", "Syria", "Iraq", "Afghanistan", "Iran", "Russia", "Azerbaijan", "Ukraine"])
        dob = f"{rng.randint(1945, 2006):04d}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"
        out.append({"name": ad, "dob": dob, "nationality": uy, "truth": {"label": "neg", "cell": "N_genel"}})
    rng.shuffle(out)
    for i, c in enumerate(out):
        c["cid"] = f"{a.set[0].upper()}{i:05d}"
    with open(os.path.join(KOK, "data", f"customers_{a.set}.jsonl"), "w", encoding="utf-8") as f:
        for c in out:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    from collections import Counter
    print(a.set, len(out), "musteri; havuz", len(havuz), "kayit")
    print(sorted(Counter(c["truth"]["cell"] for c in out).items()))


if __name__ == "__main__":
    main()
