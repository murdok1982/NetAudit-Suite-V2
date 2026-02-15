from __future__ import annotations
from datetime import datetime, timedelta
from typing import Dict, List, Iterable, Tuple
from collections import defaultdict

from .models import MessageResult, UserAggregate, Match

def risk_level_from_score(score: float) -> str:
    if score >= 12:
        return "high"
    if score >= 8:
        return "medium"
    return "low"

def aggregate_by_user(results: Iterable[MessageResult], window_minutes: int = 180) -> List[UserAggregate]:
    # Agrupa por usuario en ventana fija (últimas N horas desde cada mensaje)
    by_user: Dict[str, List[MessageResult]] = defaultdict(list)
    for r in results:
        by_user[r.user_id].append(r)

    aggs: List[UserAggregate] = []
    for user, items in by_user.items():
        items.sort(key=lambda x: x.timestamp)
        start = items[0].timestamp
        end = items[-1].timestamp
        # ventana “suave”: si hay huecos grandes, igual te conviene segmentar; aquí simplificamos
        cumulative = sum(i.risk_score for i in items)
        peak = max(i.risk_score for i in items)
        lvl = risk_level_from_score(max(peak, cumulative / max(len(items), 1)))

        # Top matches por score acumulado
        mscore = defaultdict(float)
        mobj = {}
        for it in items:
            for m in it.matches:
                key = (m.kind, m.value)
                mscore[key] += m.score
                mobj[key] = m
        top = sorted(mscore.items(), key=lambda kv: kv[1], reverse=True)[:10]
        top_matches = []
        for (k, v), s in top:
            mm = mobj[(k, v)]
            top_matches.append(Match(kind=k, value=v, score=round(s, 2), details=mm.details))

        flags = []
        if peak >= 12:
            flags.append("peak_high_message")
        if cumulative >= 30:
            flags.append("sustained_risk")

        aggs.append(UserAggregate(
            user_id=user,
            window_start=start,
            window_end=end,
            total_messages=len(items),
            cumulative_risk=round(cumulative, 2),
            peak_risk=round(peak, 2),
            risk_level=lvl,
            top_matches=top_matches,
            flags=flags
        ))

    return aggs
