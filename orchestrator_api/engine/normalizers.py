from __future__ import annotations
import re
import regex as regx
from typing import Dict, Any

AR_DIACRITICS = regx.compile(r"[\p{Mn}\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
AR_KASHIDA = "\u0640"

def normalize_arabic(text: str, opts: Dict[str, Any]) -> str:
    t = text
    if opts.get("remove_diacritics", True):
        t = AR_DIACRITICS.sub("", t)
    if opts.get("normalize_kashida", True):
        t = t.replace(AR_KASHIDA, "")
    if opts.get("normalize_alef", True):
        t = re.sub(r"[إأآا]", "ا", t)
    if opts.get("normalize_hamza", True):
        t = re.sub(r"[ؤئ]", "ء", t)
    if opts.get("normalize_teh_marbuta", True):
        t = t.replace("ة", "ه")
    return t

def normalize_common(text: str) -> str:
    t = text.lower()
    t = regx.sub(r"\s+", " ", t).strip()
    return t

def decode_arabizi_digits(text: str, digit_map: Dict[str, str]) -> str:
    # Sustituye dígitos tipo leet árabe: 7->ح etc
    t = text
    for d, ar in digit_map.items():
        t = t.replace(d, ar)
    return t

def normalize_leetspeak_basic(text: str) -> str:
    # Leet genérico (no árabe) para evasión básica
    table = str.maketrans({
        "@": "a", "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t",
        "$": "s", "!": "i"
    })
    return text.translate(table)

def normalize_text(text: str, lang_cfg: Dict[str, Any]) -> Dict[str, str]:
    raw = text
    t = normalize_common(raw)
    t_leet = normalize_leetspeak_basic(t)

    # Arabizi: mapeo de dígitos a letras árabes + mantenemos versión extra
    arabizi_cfg = (lang_cfg.get("arabizi") or {})
    digit_map = arabizi_cfg.get("digit_map") or {}

    t_arabizi = decode_arabizi_digits(t_leet, digit_map) if digit_map else t_leet

    # Árabe: normalización ortográfica
    if lang_cfg.get("language") == "ar":
        opts = (lang_cfg.get("normalization") or {})
        t_ar = normalize_arabic(t_arabizi, opts)
        return {"base": t_ar, "leet": t_leet, "arabizi": t_arabizi}
    else:
        return {"base": t_arabizi, "leet": t_leet, "arabizi": t_arabizi}
