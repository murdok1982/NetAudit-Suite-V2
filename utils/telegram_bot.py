import os
import requests
from loguru import logger

class TelegramBot:
    def __init__(self, token=None, chat_id=None):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    @property
    def is_configured(self):
        return bool(self.token and self.chat_id and "TU_TOKEN" not in self.token)

    def send_message(self, text, parse_mode="Markdown"):
        if not self.is_configured:
            logger.warning("Telegram not configured. Skipping message.")
            return None
        
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": parse_mode}
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return None

    def send_document(self, file_path, caption=""):
        if not self.is_configured or not os.path.exists(file_path):
            logger.warning("Telegram not configured or file not found.")
            return None
            
        url = f"{self.base_url}/sendDocument"
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    url, 
                    data={"chat_id": self.chat_id, "caption": caption}, 
                    files={"document": f},
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to send Telegram document: {e}")
            return None
