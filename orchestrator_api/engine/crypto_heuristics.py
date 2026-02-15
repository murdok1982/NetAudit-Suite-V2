from __future__ import annotations
import re
import base64
import math
from typing import Dict, Any

B64_RE = re.compile(r"(?:[A-Za-z0-9+/]{16,}={0,2})")
HEX_RE = re.compile(r"\b(?:0x)?[0-9a-fA-F]{20,}\b")
URLENC_RE = re.compile(r"(?:%[0-9a-fA-F]{2}){6,}")

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    ent = 0.0
    n = len(s)
    for c in freq.values():
        p = c / n
        ent -= p * math.log2(p)
    return ent

def looks_base64(token: str) -> bool:
    if len(token) % 4 != 0:
        return False
    try:
        base64.b64decode(token, validate=True)
        return True
    except Exception:
        return False

def crypto_signals(text: str) -> Dict[str, Any]:
    signals = {
        "b64_candidates": [],
        "hex_candidates": [],
        "urlenc_candidates": [],
        "high_entropy_tokens": [],
        "score": 0.0,
    }

    # base64
    for m in B64_RE.finditer(text):
        tok = m.group(0)
        if looks_base64(tok):
            signals["b64_candidates"].append(tok[:60])
    # hex
    for m in HEX_RE.finditer(text):
        signals["hex_candidates"].append(m.group(0)[:60])
    # url-encoding
    for m in URLENC_RE.finditer(text):
        signals["urlenc_candidates"].append(m.group(0)[:60])

    # tokens entropía alta
    for tok in re.findall(r"[A-Za-z0-9+/=%]{20,}", text):
        ent = shannon_entropy(tok)
        if ent >= 4.2:
            signals["high_entropy_tokens"].append({"tok": tok[:40], "entropy": round(ent, 2)})

    # scoring defensivo (no “desciframos”, solo marcamos obfuscación)
    score = 0.0
    score += 1.2 * min(len(signals["b64_candidates"]), 3)
    score += 0.9 * min(len(signals["hex_candidates"]), 3)
    score += 0.8 * min(len(signals["urlenc_candidates"]), 3)
    score += 0.6 * min(len(signals["high_entropy_tokens"]), 5)
    signals["score"] = round(score, 2)
    return signals
