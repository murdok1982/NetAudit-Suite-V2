from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class Match(BaseModel):
    kind: str
    value: str
    score: float
    details: Dict[str, Any] = {}

class MessageResult(BaseModel):
    message_id: str
    user_id: str
    language: str
    raw_text: str
    normalized_text: str
    timestamp: datetime
    risk_score: float
    risk_level: str
    matches: List[Match]
    crypto_signals: Dict[str, Any]
    notes: List[str]

class UserAggregate(BaseModel):
    user_id: str
    window_start: datetime
    window_end: datetime
    total_messages: int
    cumulative_risk: float
    peak_risk: float
    risk_level: str
    top_matches: List[Match]
    flags: List[str]
