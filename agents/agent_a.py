from .base_agent import BaseAgent

class PsychologicalAgent(BaseAgent):
    PROMPT = """
    Eres un experto en análisis clínico y forense de psicología criminal y radicalismos.
    Evalúa el siguiente contenido (mensajes de Telegram) detectando señales de comportamiento comunicativo, coerción, estafa, grooming, incitación o patrones de persuasión.
    Identifica rasgos clínicos y atribuye un nivel de riesgo conductual.
    Output: JSON con campos [summary, risk_assessment, indicators, confidence, recommended_actions]
    """

    def analyze(self, text: str) -> str:
        return self._call_llm(self.PROMPT, text)
