#!/usr/bin/env python3
"""Ad normalizasyonu ve varyant ureticileri (deterministik; rastgelelik cagirandan gelen random.Random ile).

norm(s)          : eslestirme icin katlama (Turkce buyuk/kucuk harf, aksan, noktalama)
tr_arap(name)    : Arapca/Farsca kokenli latin yaziminin Turkce imla ile yazimi (Muhammad Abd al-Rahman -> Muhammed Abdurrahman)
kiril_tr(name)   : Kiril adin Turkce romanizasyonu (Владимир Путин -> Vladimir Putin, Евгений -> Yevgeniy)
sira_kismi(name) : ad sirasi / orta ad dusurme (Turk kimlik kartindaki SOYAD AD ve patronim dusmesi)
yazim_hatasi(name, rng): 1-2 karakter hatasi + Turkce buyuk harf
"""
import re
import unicodedata

from unidecode import unidecode

# ---------------------------------------------------------------- normalizasyon

def tr_lower(s):
    return s.replace("I", "ı").replace("İ", "i").lower()


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = unidecode(tr_lower(s))
    s = s.lower().replace("'", "").replace("`", "")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _cap(tok):
    return tok[:1].replace("i", "İ").upper() + tok[1:] if tok else tok


# ---------------------------------------------------------------- Arapca kokenli -> Turkce imla

SOZLUK = {
    "muhammad": "muhammed", "mohammad": "muhammed", "mohammed": "muhammed", "mohamed": "muhammed",
    "mohamad": "muhammed", "muhammed": "muhammed", "mohd": "muhammed", "mehmood": "mahmut",
    "ahmad": "ahmet", "ahmed": "ahmet", "mahmoud": "mahmut", "mahmud": "mahmut", "mostafa": "mustafa",
    "husayn": "hüseyin", "hussein": "hüseyin", "husain": "hüseyin", "hussain": "hüseyin", "hosein": "hüseyin",
    "hossein": "hüseyin", "husein": "hüseyin", "hassan": "hasan", "hasan": "hasan", "umar": "ömer", "omar": "ömer",
    "uthman": "osman", "othman": "osman", "usman": "osman", "yousef": "yusuf", "youssef": "yusuf", "yousif": "yusuf",
    "yusif": "yusuf", "yousuf": "yusuf", "ibrahim": "ibrahim", "ebrahim": "ibrahim", "ismail": "ismail", "ismael": "ismail",
    "khalid": "halit", "khaled": "halit", "khalil": "halil", "abdallah": "abdullah", "abdullah": "abdullah", "abdulla": "abdullah",
    "abu": "ebu", "abou": "ebu", "saeed": "said", "saed": "said", "sayyid": "seyit", "sayed": "seyit", "seyed": "seyit",
    "sayyed": "seyit", "jamal": "cemal", "gamal": "cemal", "jalal": "celal", "karim": "kerim", "kareem": "kerim",
    "rashid": "reşit", "rasheed": "reşit", "hamid": "hamit", "hameed": "hamit", "majid": "mecit", "nasser": "nasır",
    "nasir": "nasır", "naser": "nasır", "faisal": "faysal", "fatima": "fatma", "aisha": "ayşe", "ayesha": "ayşe",
    "zaynab": "zeynep", "zainab": "zeynep", "khadija": "hatice", "amina": "emine", "jafar": "cafer", "jaafar": "cafer",
    "qasim": "kasım", "qassem": "kasım", "kassem": "kasım", "qassim": "kasım", "tariq": "tarık", "tarek": "tarık",
    "saleh": "salih", "salih": "salih", "sulayman": "süleyman", "suleiman": "süleyman", "sulaiman": "süleyman",
    "zakariya": "zekeriya", "zakaria": "zekeriya", "idris": "idris", "harun": "harun", "haroun": "harun", "noor": "nur",
    "hamza": "hamza", "hamzah": "hamza", "anwar": "enver", "anas": "enes", "bilal": "bilal", "mansour": "mansur",
    "mansur": "mansur", "nabil": "nebil", "walid": "velid", "waleed": "velid", "yasin": "yasin", "yaseen": "yasin",
    "zubair": "zübeyir", "zubayr": "zübeyir", "jihad": "cihat", "ayman": "eymen", "osama": "üsame", "usama": "üsame",
    "ammar": "ammar", "abbas": "abbas", "hadi": "hadi", "mahdi": "mehdi", "mehdi": "mehdi", "akram": "ekrem",
    "adel": "adil", "adil": "adil", "fadel": "fazıl", "fadil": "fazıl", "hakim": "hakim", "habib": "habip",
    "latif": "latif", "aziz": "aziz", "rahman": "rahman", "rahim": "rahim", "qadir": "kadir", "qader": "kadir",
    "salam": "selam", "salem": "salim", "salim": "salim", "sharif": "şerif", "shareef": "şerif", "shaikh": "şeyh",
    "sheikh": "şeyh", "shaykh": "şeyh", "mullah": "molla", "mulla": "molla", "haji": "hacı", "hajji": "hacı",
}
DIN = {"salah": "selahattin", "nur": "nurettin", "noor": "nurettin", "izz": "izzettin", "ala": "alaattin",
       "alaa": "alaattin", "jamal": "cemalettin", "kamal": "kemalettin", "nasir": "nasırettin", "nasser": "nasırettin",
       "shams": "şemsettin", "sayf": "seyfettin", "saif": "seyfettin", "sharaf": "şerafettin", "fakhr": "fahrettin",
       "badr": "bedrettin", "zain": "zeynettin", "zayn": "zeynettin", "muhyi": "muhyittin", "qutb": "kutbettin"}
GUNES = set("rsştdzlnc")  # Turkce Abdü- ilgi takisinda ikizlesen sessizler


def _harf_kurallari(t):
    t = t.replace("kh", "h").replace("sh", "ş").replace("ch", "ç").replace("dh", "z").replace("th", "s")
    t = t.replace("gh", "g").replace("ou", "u").replace("ee", "i").replace("oo", "u").replace("aa", "a")
    t = t.replace("q", "k").replace("w", "v").replace("j", "c").replace("x", "ks")
    t = re.sub(r"(.)\1\1+", r"\1\1", t)
    if t.endswith("ah") and len(t) > 4 and not t.endswith("llah"):
        t = t[:-1]
    return t


def _tok_tr(t):
    t = t.lower()
    return SOZLUK.get(t) or _harf_kurallari(t)


def tr_arap(name, rng=None):
    """Latin harfli Arapca/Farsca kokenli adi Turkce imlaya cevirir. Degisiklik yoksa None."""
    toks = [x for x in re.split(r"[\s\-]+", name.replace("'", "").replace("`", "")) if x]
    out, i = [], 0
    while i < len(toks):
        t = toks[i].lower()
        nxt = toks[i + 1].lower() if i + 1 < len(toks) else None
        # Abd al-Rahman / Abdul Rahman / Abdel Aziz -> Abdurrahman / Abdülaziz
        if t in ("abd", "abdul", "abdel", "abdal", "abdol", "abdur", "abdu") and nxt:
            j = i + 1
            if nxt in ("al", "el", "ul", "ar", "as", "an", "az", "ad", "at") and i + 2 < len(toks):
                j = i + 2
            x = _tok_tr(toks[j])
            if x[:1] == "r":
                out.append("abdur" + x)
            elif x[:1] in GUNES:
                out.append("abdü" + x[0] + x)
            else:
                out.append("abdül" + x)
            i = j + 1
            continue
        if t.startswith("abdul") and len(t) > 6:  # Abdulrahman tek kelime
            x = _tok_tr(t[5:])
            out.append(("abdur" + x) if x[:1] == "r" else ("abdül" + x))
            i += 1
            continue
        # Salah al-Din / Nur ud-Din -> Selahattin / Nurettin
        if t in DIN and nxt in ("al", "el", "ud", "ad", "ed", "uddin", "aldin", "eddin", "addin", "din", "deen"):
            j = i + 1
            if nxt in ("al", "el", "ud", "ad", "ed") and i + 2 < len(toks) and toks[i + 2].lower() in ("din", "deen"):
                j = i + 2
            out.append(DIN[t])
            i = j + 1
            continue
        if t in ("al", "el") and nxt:  # artikel: soyaddan dusur ya da El- birak
            if rng is not None and rng.random() < 0.5:
                out.append("el")
            i += 1
            continue
        if t.startswith(("al-", "el-")):
            t = t[3:]
        out.append(_tok_tr(t))
        i += 1
    res = " ".join(_cap(x) for x in out if x)
    return res if norm(res) != norm(name) else None


# ---------------------------------------------------------------- Kiril -> Turkce romanizasyon

KIRIL = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "j", "з": "z", "и": "i",
         "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
         "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ç", "ш": "ş", "щ": "şç", "ъ": "", "ы": "ı", "ь": "",
         "э": "e", "ю": "yu", "я": "ya", "і": "i", "ї": "yi", "є": "ye", "ґ": "g", "ў": "v"}
SESLI = set("аеёиоуыэюяіїє")


def kiril_tr(name):
    if not re.search(r"[Ѐ-ӿ]", name or ""):
        return None
    words = []
    for w in re.split(r"[\s\-]+", name.strip()):
        w = w.lower()
        if not w:
            continue
        r = []
        for k, ch in enumerate(w):
            if ch == "е" and (k == 0 or w[k - 1] in SESLI or w[k - 1] in "ьъ"):
                r.append("ye")
            elif ch == "и" and k + 1 < len(w) and w[k + 1] == "й" and k + 2 == len(w):
                r.append("i")  # -ий -> -iy
            else:
                r.append(KIRIL.get(ch, ch))
        words.append("".join(r))
    res = " ".join(_cap(x) for x in words if x)
    return res or None


# ---------------------------------------------------------------- sira / kismi ad

def sira_kismi(name, rng):
    toks = name.split()
    if len(toks) >= 3:
        # patronim / orta adi dusur: ilk ad + son ad
        res = [toks[0], toks[-1]]
        if rng.random() < 0.5:
            res = [tr_upper(toks[-1]), toks[0]]  # SOYAD Ad
        return " ".join(res)
    if len(toks) == 2:
        return " ".join([tr_upper(toks[1]), toks[0]])
    return None


# ---------------------------------------------------------------- yazim hatasi

KLAVYE = {"a": "sq", "s": "ad", "d": "sf", "e": "wr", "r": "et", "i": "uo", "o": "ip", "u": "yi", "n": "bm",
          "m": "n", "h": "gj", "k": "jl", "l": "k", "t": "ry", "y": "tu", "b": "vn", "g": "fh", "z": "x"}


def yazim_hatasi(name, rng):
    toks = name.split()
    aday = [i for i, t in enumerate(toks) if len(t) >= 5]
    if not aday:
        return None
    for _ in range(1 if rng.random() < 0.6 else 2):
        i = rng.choice(aday)
        t = toks[i]
        p = rng.randrange(1, len(t) - 1)
        op = rng.choice(["sil", "degistir", "yer", "cift"])
        if op == "sil":
            t = t[:p] + t[p + 1:]
        elif op == "degistir":
            c = t[p].lower()
            t = t[:p] + rng.choice(KLAVYE.get(c, "e")) + t[p + 1:]
        elif op == "yer":
            t = t[:p] + t[p + 1] + t[p] + t[p + 2:]
        else:
            t = t[:p] + t[p] + t[p:]
        toks[i] = t
    res = tr_upper(" ".join(toks))
    return res if norm(res) != norm(name) else None


if __name__ == "__main__":
    import random
    r = random.Random(1)
    for n in ["Muhammad Abd al-Rahman AL-HASSAN", "Salah al-Din Khalil", "Abdulrahman Yousef Qassem",
              "Husayn Ali al-Tikriti", "MOHAMMAD ALEEM NOORANI"]:
        print(n, "->", tr_arap(n, r))
    for n in ["Владимир Владимирович Путин", "Казаков Виктор Алексеевич", "Евгений Юрьевич Ерёменко"]:
        print(n, "->", kiril_tr(n))
    print(sira_kismi("Vladimir Vladimirovich PUTIN", r), "|", yazim_hatasi("Viktor Alekseevich KAZAKOV", r))
    print(norm("MUHAMMED ABDURRAHMAN Şİmşek"), "|", norm("Abd al-Rahman"))
