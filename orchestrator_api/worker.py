from celery import Celery
import os
import yaml
from engine.detector import analyze_message
import models, database, agents_connector
from datetime import datetime, timedelta

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
RULES_DIR = os.getenv("RULES_DIR", "./rules")

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

# Simple cache for language configurations
LANG_CONFIGS = {}

def load_lang_configs():
    if not os.path.exists(RULES_DIR):
        print(f"Warning: Rules directory {RULES_DIR} not found.")
        return
    for filename in os.listdir(RULES_DIR):
        if filename.endswith(".yaml"):
            lang = filename.split(".")[0]
            with open(os.path.join(RULES_DIR, filename), 'r', encoding='utf-8') as f:
                LANG_CONFIGS[lang] = yaml.safe_load(f)

load_lang_configs()

@celery_app.task(name="analyze_message")
def analyze_message_task(message_id: int):
    db = next(database.get_db())
    msg = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not msg:
        return

    lang = msg.lang or "en"
    lang_cfg = LANG_CONFIGS.get(lang, LANG_CONFIGS.get("en", {}))

    # Run advanced analysis
    result = analyze_message(
        message_id=str(msg.telegram_id),
        user_id=msg.user_hash,
        text=msg.text,
        lang=lang,
        lang_cfg=lang_cfg,
        timestamp=msg.timestamp
    )

    # Update message with new score and metadata
    msg.risk_score = result.risk_score
    msg.metadata_json = {
        **(msg.metadata_json or {}),
        "engine_analysis": result.dict()
    }
    db.commit()

    # Create case if threshold exceeded (using the new risk level or score)
    if result.risk_score >= 12.0 or result.risk_level in ["high", "medium"]:
        create_case_task.delay(msg.id, result.risk_score)

@celery_app.task(name="create_case")
def create_case_task(message_id: int, score: float):
    db = next(database.get_db())
    msg = db.query(models.Message).filter(models.Message.id == message_id).first()
    
    # Check if a case already exists for this user hash in the last 6 hours
    six_hours_ago = datetime.utcnow() - timedelta(hours=6)
    existing_case = db.query(models.Case).filter(
        models.Case.user_hash == msg.user_hash,
        models.Case.created_at >= six_hours_ago,
        models.Case.status != "closed"
    ).first()

    if existing_case:
        # Update existing case risk if higher
        if score > existing_case.risk_score:
            existing_case.risk_score = score
        db.commit()
    else:
        new_case = models.Case(
            user_hash=msg.user_hash,
            risk_score=score,
            initial_message_id=msg.id,
            status="open"
        )
        db.add(new_case)
        db.commit()
        db.refresh(new_case)

        # Trigger Agent Analysis
        agents_connector.run_agent_analysis.delay(new_case.id)
