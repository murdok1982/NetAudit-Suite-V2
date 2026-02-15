import openai
import os
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, model="gpt-4"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model
        openai.api_key = self.api_key

    @abstractmethod
    def analyze(self, input_data: str) -> str:
        pass

    def _call_llm(self, system_prompt: str, user_content: str) -> str:
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in LLM call: {str(e)}"
