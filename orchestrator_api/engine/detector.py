from __future__ import annotations
from typing import Dict, Any, List, Tuple
from datetime import datetime
import regex as regx
from rapidfuzz import fuzz

from .models import Match, MessageResult
from .normalizers import normalize_text
from .crypto_heuristics import crypto_signals
from .correlator import risk_level_from_score

def compile_regex_list(patterns: List[str]) -> List[regx.Pattern]:
    compiled = []
    for p in patterns:
        compiled.append(regx.compile(p, flags=regx.IGNORECASE))
    return compiled

def fuzzy_hits(text: str, items: List[str], threshold: int = 92) -> List[str]:
    hits = []
    for it in items:
        if len(it) < 4:
            continue
        score = fuzz.partial_ratio(text, it.lower())
        if score >= threshold:
            hits.append(it)
    return hits

def find_phrase_hits(text: str, items: List[str]) -> List[str]:
    hits = []
    for it in items:
        if it.lower() in text:
            hits.append(it)
    return hits

def build_matches(raw_text: str, lang_cfg: Dict[str, Any]) -> Tuple[str, List[Match], Dict[str, str]]:
    norm = normalize_text(raw_text, lang_cfg)
    text = norm["base"]

    matches: List[Match] = []

    def add(kind: str, value: str, score: float, **details):
        matches.append(Match(kind=kind, value=value, score=score, details=details or {}))

    # Emojis
    emo = (lang_cfg.get("emoji_indicators") or {})
    emo_items = emo.get("items") or []
    emo_weight = float(emo.get("weight", 0.0))
    for e in emo_items:
        if e in raw_text:
            add("emoji", e, emo_weight, group="emoji_indicators")

    # High risk phrases (literal + fuzzy)
    phr = (lang_cfg.get("phrases_high_risk") or {})
    phr_items = phr.get("items") or []
    phr_weight = float(phr.get("weight", 0.0))
    for it in find_phrase_hits(text, [x.lower() for x in phr_items]):
        add("phrase_high", it, phr_weight)

    # Medium keywords
    kw = (lang_cfg.get("keywords_medium_risk") or {})
    kw_items = kw.get("items") or []
    kw_weight = float(kw.get("weight", 0.0))
    for it in find_phrase_hits(text, [x.lower() for x in kw_items]):
        add("keyword_medium", it, kw_weight)

    # Regex indicators
    rx = (lang_cfg.get("regex_indicators") or {})
    rx_items = rx.get("items") or []
    rx_weight = float(rx.get("weight", 0.0))
    for cre in compile_regex_list(rx_items):
        if cre.search(text):
            add("regex", cre.pattern, rx_weight)

    # Euphemisms + slang
    eup = (lang_cfg.get("euphemisms") or {})
    eup_items = eup.get("items") or []
    eup_weight = float(eup.get("weight", 0.0))
    for it in fuzzy_hits(text, [x.lower() for x in eup_items], threshold=94):
        add("euphemism", it, eup_weight)

    slang = (lang_cfg.get("slang_regional") or {})
    slang_weight = float(slang.get("weight", 0.0))
    if isinstance(slang, dict) and "items" not in slang:
        for region, items in slang.items():
            if region == "weight":
                continue
            for it in find_phrase_hits(text, [x.lower() for x in (items or [])]):
                add("slang", it, slang_weight, region=region)
    else:
        for it in find_phrase_hits(text, [x.lower() for x in slang.get("items", [])]):
            add("slang", it, slang_weight)

    # Arabizi patterns
    arabizi = (lang_cfg.get("arabizi") or {})
    a_weight = float(arabizi.get("weight", 0.0))
    a_patterns = arabizi.get("patterns") or []
    for cre in compile_regex_list(a_patterns):
        if cre.search(norm["leet"]):
            add("arabizi_pattern", cre.pattern, a_weight)

    # Behavioral patterns
    bp = (lang_cfg.get("behavioral_patterns") or {})
    bp_weight = float(bp.get("weight", 0.0))
    for grp in ("intent_markers", "recruitment_markers", "logistics_markers"):
        for it in (bp.get(grp) or []):
            if it.lower() in text:
                add("behavior", it, bp_weight, subtype=grp)

    return text, matches, norm

def compute_score(matches, crypto_sig, bucket_weights: Dict[str, float]) -> float:
    score = sum(m.score for m in matches)
    score += 0.7 * crypto_sig.get("score", 0.0)

    kinds = {m.kind for m in matches}
    if "phrase_high" in kinds or "behavior" in kinds:
        score += bucket_weights.get("terrorism_operational_intent", 0.0)
    if "slang" in kinds or "euphemism" in kinds:
        score += bucket_weights.get("drugs_trafficking", 0.0) * 0.3

    return round(score, 2)

def extract_bucket_weights(lang_cfg: Dict[str, Any]) -> Dict[str, float]:
    out = {}
    for b in (lang_cfg.get("topic_buckets") or []):
        out[b.get("category")] = float(b.get("weight", 0.0))
    return out

def analyze_message(
    message_id: str,
    user_id: str,
    text: str,
    lang: str,
    lang_cfg: Dict[str, Any],
    timestamp: datetime | None = None
) -> MessageResult:
    ts = timestamp or datetime.utcnow()

    normalized_text, matches, norm_versions = build_matches(text, lang_cfg)
    crypto_sig = crypto_signals(text)

    bucket_weights = extract_bucket_weights(lang_cfg)
    score = compute_score(matches, crypto_sig, bucket_weights)
    level = risk_level_from_score(score)

    notes = []
    if crypto_sig.get("score", 0) >= 3:
        notes.append("obfuscation_suspected")
    if any(m.kind == "arabizi_pattern" for m in matches):
        notes.append("arabizi_detected")

    return MessageResult(
        message_id=message_id,
        user_id=user_id,
        language=lang,
        raw_text=text,
        normalized_text=normalized_text,
        timestamp=ts,
        risk_score=score,
        risk_level=level,
        matches=sorted(matches, key=lambda m: m.score, reverse=True),
        crypto_signals=crypto_sig,
        notes=notes,
    )
