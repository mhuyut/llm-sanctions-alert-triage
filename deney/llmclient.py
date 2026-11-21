#!/usr/bin/env python3
"""LLM client for arxiv-kyc-llm (arxiv-harness-uyum kopyasi, stdlib only).

EVREN: ana + yedek hesap (02.10.2026 onayi); yedekte EVREN_YEDEK_REZERV kadar token diger projelere birakilir.
Dakikalik 429 da bekle-yeniden dene; gunluk kota dolunca cagri "KOTA" doner, runner sonra devam eder.
Her cagrida X-Evren-Credits-Remaining basligi usage.jsonl dosyasina yazilir (Kasim 2026 sonrasi maliyet olcumu).

Backends
  evren  : EVREN LLM API (OpenAI-compatible, domestic). Keys are read from files, never printed.
  ollama : local Ollama server (http://localhost:11434, native /api/chat).

Every call returns a dict with the raw text, latency and token usage. Nothing secret is logged.
"""
import json, os, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "tfsc-llm-credit"))
EVREN_BASE = "https://evren-llmapi.ssyz.org.tr/v1"
OLLAMA_BASE = "http://localhost:11434"

# model id -> key file (same mapping as earlier projects)
EVREN_KEYS = {
    "glm-5.3": ".api_key_evren",
    "deepseek-v4-flash": ".api_key_evren_deepseek",
    "deepseek-v4.1-flash": ".api_key_evren_all",
    "qwen3.8-flash-next": ".api_key_evren_qwen",
    "gemma-4-31b": ".api_key_evren_gemma",
}
EVREN_MODELS = list(EVREN_KEYS)
OLLAMA_MODELS = ["qwen3.8:27b-mxfp8", "qwen3.6:35b", "gemma4:31b", "gpt-oss:20b"]

_keys = {}
BACKUP_KEY_FILE = ".api_key_evren_yedek"  # yedek anahtar: asil anahtar kotasi bitince otomatik gecilir
_switched = set()


def _switch_to_backup(model):
    return False  # hesap gecisi hesap_sec() ile yapilir


def _key(model):
    if model not in _keys and os.environ.get("EVREN_FORCE_BACKUP") == "1":
        _switch_to_backup(model)
    if model not in _keys:
        fn = ".api_key_evren_all"  # tum modeller hesap 1
        path = os.path.join(KEY_DIR, fn)
        if not os.path.exists(path):
            path = os.path.join(KEY_DIR, ".api_key_evren_all")
        with open(path) as f:
            _keys[model] = f.read().strip()
    return _keys[model]


# --- Iki hesap (02.10.2026, Mehmet'in onayi): once ana hesap, bitince yedek hesap.
# Yedek hesapta diger projeler (ai-agent-delegation, ssci-multimodal-risk) icin REZERV token birakilir; sifirlanmaya
# 3 saatten az kaldiysa rezerv uygulanmaz (kullanilmayan kota zaten yanar). EVREN_HESAP=ana|yedek|ikisi (varsayilan ikisi).
HESAP_DOSYA = {"ana": ".api_key_evren_all", "yedek": ".api_key_evren_yedek"}
REZERV = {"ana": 0, "yedek": int(os.environ.get("EVREN_YEDEK_REZERV", "2500000"))}
ASGARI = 40000
_kota_onbellek = {}
_hesap_anahtar = {}
import threading as _th
_kilit = _th.Lock()


def _hesap_key(h):
    if h not in _hesap_anahtar:
        with open(os.path.join(KEY_DIR, HESAP_DOSYA[h])) as f:
            _hesap_anahtar[h] = f.read().strip()
    return _hesap_anahtar[h]


def kota(h, tazele=False):
    """/v1/quota: {'kalan', 'sifirlanma'(datetime)} — 60 sn onbellek."""
    import datetime as _dt
    now = time.time()
    with _kilit:
        c = _kota_onbellek.get(h)
        if c and not tazele and now - c["t"] < 60:
            return c
    try:
        req = urllib.request.Request(EVREN_BASE + "/quota", headers={"Authorization": "Bearer " + _hesap_key(h)})
        with urllib.request.urlopen(req, timeout=20) as r:
            q = json.load(r)
        kalan = int(q.get("daily_limit_tokens") or 0) - int(q.get("daily_used_tokens") or 0)
        sif = _dt.datetime.fromisoformat(str(q.get("daily_reset_at")).replace("Z", "+00:00"))
    except Exception:
        kalan, sif = (c["kalan"], c["sifirlanma"]) if c else (10**9, None)
    c = {"t": now, "kalan": kalan, "sifirlanma": sif}
    with _kilit:
        _kota_onbellek[h] = c
    return c


def hesap_sec():
    import datetime as _dt
    secim = os.environ.get("EVREN_HESAP", "ikisi")
    sira = ["ana", "yedek"] if secim == "ikisi" else [secim]
    for h in sira:
        c = kota(h)
        rez = REZERV[h]
        if c["sifirlanma"] is not None and (c["sifirlanma"] - _dt.datetime.now(_dt.timezone.utc)).total_seconds() < 3 * 3600:
            rez = 0
        if c["kalan"] - rez > ASGARI:
            return h
    return None


def _hesap_bitti(h):
    with _kilit:
        c = _kota_onbellek.get(h) or {}
        _kota_onbellek[h] = {"t": time.time(), "kalan": 0, "sifirlanma": c.get("sifirlanma")}


def backend_of(model):
    return "ollama" if ":" in model else "evren"


SON_KREDI = {"kalan": None}  # son yanittaki X-Evren-Credits-Remaining


def _post(url, body, headers, timeout):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        if "evren" in url and r.headers.get("X-Evren-Credits-Remaining") is not None:
            SON_KREDI["kalan"] = r.headers.get("X-Evren-Credits-Remaining")
        return json.load(r)


KOTA = {"bitti": False}  # EVREN gunluk token kotasi asildiginda True; sonraki EVREN cagrilari HTTP'ye gitmeden "KOTA" doner


KOK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def duraklat_bekle():
    """Is birlikci duraklatma (EVREN Paneli): proje kokunde DURAKLAT dosyasi varken yeni EVREN istegi gonderilmez."""
    yazdi = False
    while os.path.exists(os.path.join(KOK, "DURAKLAT")):
        if not yazdi:
            print("[llmclient] DURAKLAT var; bekleniyor", flush=True)
            yazdi = True
        time.sleep(15)


def _kullanim_yaz(path, model, hesap, u):
    try:
        os.makedirs(os.path.join(KOK, "logs"), exist_ok=True)
        with open(os.path.join(KOK, "logs", "usage.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.time(), "tag": "kyc", "path": path, "acct": 0 if hesap == "ana" else 1, "model": model,
                                "prompt": u.get("prompt_tokens"), "completion": u.get("completion_tokens"),
                                "total": u.get("total_tokens"), "kredi": SON_KREDI["kalan"]}) + "\n")
    except Exception:
        pass


def chat(model, messages, max_tokens=512, temperature=0.0, seed=7, timeout=300, retries=6, json_mode=False, num_ctx=8192):
    """One chat completion. Returns dict(text, latency_s, in_tok, out_tok, served_model, error)."""
    be = backend_of(model)
    last = None
    hesap = None
    if be == "evren":
        hesap = hesap_sec()
        if hesap is None or KOTA["bitti"]:
            KOTA["bitti"] = True
            return {"text": "", "latency_s": None, "in_tok": None, "out_tok": None, "served_model": None, "hesap": None,
                    "error": "KOTA daily_token_limit_exceeded"}
    dakika_bekleme = 0  # dakikalik token sinirinda (429, gunluk kota degil) bekle-yeniden dene; deneme sayisindan dusmez
    attempt = 0
    while attempt < retries:
        attempt += 1
        t0 = time.time()
        try:
            if be == "evren":
                body = {"model": model, "messages": messages, "temperature": temperature,
                        "max_tokens": max_tokens, "seed": seed,
                        "chat_template_kwargs": {"enable_thinking": False}}
                if json_mode:
                    body["response_format"] = {"type": "json_object"}
                if model.startswith("glm"):
                    body["thinking"] = {"type": "disabled"}  # glm-5.3 enable_thinking'i yok sayiyor (13.10.2026 notu)
                h = {"Content-Type": "application/json", "Authorization": "Bearer " + _hesap_key(hesap)}
                duraklat_bekle()
                r = _post(EVREN_BASE + "/chat/completions", body, h, timeout)
                msg = r["choices"][0]["message"]
                u = r.get("usage") or {}
                _kullanim_yaz("chat/completions", model, hesap, u)
                return {"text": msg.get("content") or "", "latency_s": round(time.time() - t0, 3),
                        "in_tok": u.get("prompt_tokens"), "out_tok": u.get("completion_tokens"),
                        "served_model": r.get("model"), "hesap": hesap, "error": None}
            else:
                body = {"model": model, "messages": messages, "stream": False,
                        "options": {"temperature": temperature, "seed": seed, "num_predict": max_tokens,
                                    "num_ctx": num_ctx},
                        "think": ("low" if model.startswith("gpt-oss") else False)}
                if json_mode and not model.startswith("gpt-oss"):
                    body["format"] = "json"
                r = _post(OLLAMA_BASE + "/api/chat", body, {"Content-Type": "application/json"}, timeout)
                msg = r.get("message", {})
                return {"text": msg.get("content") or "", "latency_s": round(time.time() - t0, 3),
                        "in_tok": r.get("prompt_eval_count"), "out_tok": r.get("eval_count"),
                        "served_model": r.get("model"), "error": None}
        except urllib.error.HTTPError as e:
            code = e.code
            try:
                detail = e.read().decode("utf-8", "replace")[:400]
            except Exception:
                detail = ""
            last = f"HTTP {code} {detail}"
            if be == "evren" and code == 429 and "daily_token_limit" in detail:
                _hesap_bitti(hesap)
                yeni = hesap_sec()
                if yeni is not None:
                    print(f"[llmclient] {hesap} hesabinin gunluk kotasi doldu -> {yeni} hesabina geciliyor", flush=True)
                    hesap = yeni
                    continue
                KOTA["bitti"] = True
                print("[llmclient] EVREN iki hesapta da gunluk kota doldu; kalan EVREN cagrilari atlaniyor", flush=True)
                return {"text": "", "latency_s": None, "in_tok": None, "out_tok": None, "served_model": None, "hesap": None,
                        "error": "KOTA daily_token_limit_exceeded"}
            if be == "evren" and code == 429 and dakika_bekleme < 60:
                dakika_bekleme += 1
                attempt -= 1
                time.sleep(15 + 10 * (dakika_bekleme % 3))
                continue
            # kota/yetki/limit hatalarinda (404 disi 4xx) yedek anahtara gec
            if be == "evren" and 400 <= code < 500 and code != 404:
                if _switch_to_backup(model):
                    continue
                if code in (401, 403):  # yedek anahtar da reddedildi (or. kullanim sartlari onayi) -> bosuna bekleme
                    break
            if code in (400, 404) and attempt >= 1:
                break
            # model EVREN'de gecici olarak kapali ("saglikli endpoint yok"): 2 denemeden sonra birak, gorev sonra yeniden kosulur
            if code == 503 and ("service_unavailable" in detail or "endpoint yok" in detail) and attempt >= 1:
                break
            if code == 401:
                break
        except Exception as e:  # timeouts, connection resets
            last = repr(e)[:200]
        time.sleep(min(60, 3 * (2 ** attempt)))
    return {"text": "", "latency_s": None, "in_tok": None, "out_tok": None, "served_model": None, "error": last}


def parse_json(text):
    """Extract the first JSON object from a model reply (tolerates code fences and prose)."""
    if not text:
        return None
    t = text.strip()
    if "</think>" in t:
        t = t.split("</think>")[-1]
    t = t.replace("```json", "```")
    if "```" in t:
        parts = t.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("{") or p.startswith("["):
                t = p
                break
    s = t.find("{")
    if s < 0:
        return None
    depth, instr, esc = 0, False, False
    for i in range(s, len(t)):
        c = t[i]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = False
        else:
            if c == '"':
                instr = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(t[s:i + 1])
                    except Exception:
                        return None
    return None


def run_tasks(tasks, model, out_path, call_fn, workers=4, log_every=50):
    """Resumable runner. tasks: list of dicts with 'tid'. call_fn(task, model) -> result dict.
    Appends one JSON line per finished task to out_path."""
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed
    done = set()
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if not r.get("error"):
                        done.add(r["tid"])
                except Exception:
                    pass
    todo = [t for t in tasks if t["tid"] not in done]
    print(f"[{model}] {len(done)} done, {len(todo)} to go -> {os.path.basename(out_path)}", flush=True)
    lock = threading.Lock()
    n = 0
    t0 = time.time()
    with open(out_path, "a", encoding="utf-8") as f, ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(call_fn, t, model): t for t in todo}
        for fu in as_completed(futs):
            try:
                res = fu.result()
            except Exception as e:
                res = {"tid": futs[fu]["tid"], "model": model, "error": repr(e)[:200]}
            with lock:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")
                f.flush()
                n += 1
                if n % log_every == 0:
                    el = time.time() - t0
                    print(f"[{model}] {n}/{len(todo)}  {el/60:.1f} dk  ~{el/n*(len(todo)-n)/60:.0f} dk kaldi", flush=True)
    print(f"[{model}] bitti ({n} yeni)", flush=True)


def embed(texts, model="qwen3-embedding-8b", timeout=300, retries=5):
    """EVREN /embeddings. Returns list of vectors (same order) or raises after retries."""
    last = None
    for attempt in range(retries):
        try:
            hs = hesap_sec()
            if hs is None:
                raise RuntimeError("KOTA daily_token_limit_exceeded")
            h = {"Content-Type": "application/json", "Authorization": "Bearer " + _hesap_key(hs)}
            duraklat_bekle()
            r = _post(EVREN_BASE + "/embeddings", {"model": model, "input": texts}, h, timeout)
            _kullanim_yaz("embeddings", model, hs, r.get("usage") or {})
            data = sorted(r["data"], key=lambda d: d["index"])
            return [d["embedding"] for d in data]
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code == 429 and hs:
                _hesap_bitti(hs)
                continue
            if e.code in (400, 401, 403, 404):
                break
        except Exception as e:
            last = repr(e)[:200]
        time.sleep(min(60, 3 * (2 ** attempt)))
    raise RuntimeError("embed failed: " + str(last))


def rerank(query, documents, model="qwen3-reranker-8b", timeout=300, retries=5):
    """EVREN /rerank (Cohere/Jina style). Returns list of (index, score) sorted by score desc."""
    last = None
    for attempt in range(retries):
        try:
            hs = hesap_sec()
            if hs is None:
                raise RuntimeError("KOTA daily_token_limit_exceeded")
            h = {"Content-Type": "application/json", "Authorization": "Bearer " + _hesap_key(hs)}
            r = _post(EVREN_BASE + "/rerank", {"model": model, "query": query, "documents": documents}, h, timeout)
            res = r.get("results") or r.get("data") or []
            return sorted([(x["index"], x.get("relevance_score", x.get("score"))) for x in res], key=lambda t: -t[1])
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code == 429 and hs:
                _hesap_bitti(hs)
                continue
            if e.code in (400, 401, 403, 404):
                break
        except Exception as e:
            last = repr(e)[:200]
        time.sleep(min(60, 3 * (2 ** attempt)))
    raise RuntimeError("rerank failed: " + str(last))
