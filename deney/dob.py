#!/usr/bin/env python3
"""Dogum tarihi karsilastirmasi: politika.md madde 1'in deterministik uygulamasi.

durum(musteri_dob 'YYYY-MM-DD', liste_doblari [{y,m,d,circa}]) -> 'match' | 'minor' | 'conflict'
"""


def _tek(c, l):
    cy, cm, cd = c
    ly, lm, ld, circa = l["y"], l.get("m"), l.get("d"), l.get("circa", False)
    if lm is None or ld is None:  # yalniz yil (ya da yil+ay)
        if cy == ly and (lm is None or cm == lm):
            return "match"
        tol = 2 if circa else 1
        return "minor" if abs(cy - ly) <= tol else "conflict"
    if (cy, cm, cd) == (ly, lm, ld):
        return "match"
    if circa and abs(cy - ly) <= 2:
        return "minor"
    if cy == ly and cm == ld and cd == lm:
        return "minor"  # gun-ay yer degistirmis
    if cm == lm and cd == ld and abs(cy - ly) == 1:
        return "minor"
    a, b = f"{cy:04d}{cm:02d}{cd:02d}", f"{ly:04d}{lm:02d}{ld:02d}"
    if sum(x != y for x, y in zip(a, b)) == 1:
        return "minor"  # tek hane farki
    return "conflict"


SIRA = {"match": 0, "minor": 1, "conflict": 2}


def durum(cdob, ldobs):
    c = tuple(int(x) for x in cdob.split("-"))
    return min((_tek(c, l) for l in ldobs), key=SIRA.get) if ldobs else "unknown"


def yil_farki(cdob, ldobs):
    cy = int(cdob[:4])
    return min(abs(cy - l["y"]) for l in ldobs)


def liste_dob_metni(l):
    s = f"{l['y']:04d}" if l.get("m") is None else (f"{l['y']:04d}-{l['m']:02d}" if l.get("d") is None else f"{l['y']:04d}-{l['m']:02d}-{l['d']:02d}")
    return ("circa " + s) if l.get("circa") else s
