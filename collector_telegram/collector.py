from telethon import TelegramClient, events
import os
import hashlib
import json
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("TG_API_ID")
API_HASH = os.getenv("TG_API_HASH")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")
SALT = os.getenv("HASH_SALT", "default_salt")

client = TelegramClient('data/collector_session', API_ID, API_HASH)

def pseudonymize_user(user_id):
    if not user_id:
        return "anonymous"
    return hashlib.sha256(f"{user_id}{SALT}".encode()).hexdigest()

@client.on(events.NewMessage)
async def my_event_handler(event):
    if event.is_group or event.is_channel:
        chat = await event.get_chat()
        
        user_hash = pseudonymize_user(event.sender_id)
        
        payload = {
            "message_id": str(event.id),
            "chat_id": str(event.chat_id),
            "chat_title": getattr(chat, 'title', None),
            "user_handle_hash": user_hash,
            "text": event.message.message or "",
            "timestamp": event.date.isoformat(),
            "lang_detected": None,
            "metadata_extra": {
                "reply_to": event.reply_to_msg_id,
                "forwarded_from": str(event.fwd_from) if event.fwd_from else None,
                "entities": [ent.to_dict() for ent in (event.entities or [])]
            }
        }

        async with httpx.AsyncClient() as http_client:
            try:
                r = await http_client.post(f"{ORCHESTRATOR_URL}/ingest/message", json=payload)
                print(f"Message ingested: {r.status_code}")
            except Exception as e:
                print(f"Error sending message to orchestrator: {e}")

if __name__ == "__main__":
    print("Starting Telegram Collector...")
    client.start()
    client.run_until_disconnected()
