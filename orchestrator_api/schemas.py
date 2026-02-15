from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class MessageCreate(BaseModel):
    message_id: str
    chat_id: str
    chat_title: Optional[str]
    user_handle_hash: str
    text: str
    timestamp: datetime
    lang_detected: Optional[str]
    metadata_extra: Optional[Dict[str, Any]]

class MessageResponse(BaseModel):
    id: int
    telegram_id: str
    risk_score: float
    created_at: datetime

    class Config:
        from_attributes = True

class CaseResponse(BaseModel):
    id: int
    status: str
    risk_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True
