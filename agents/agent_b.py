from .base_agent import BaseAgent

class IntelAgent(BaseAgent):
    PROMPT = """
    Eres un experto en inteligencia y contrainteligencia, insurgencias y operaciones híbridas.
    Evalúa si el contenido sugiere amenazas a la integridad/infraestructura, campañas narrativas coordinadas, desinformación o coerción.
    Identifica objetivos, temas y técnicas de manipulación.
    Output: JSON con campos [summary, danger_level, techniques, objectives, mapping_mitre]
    """

    def analyze(self, text: str) -> str:
        return self._call_llm(self.PROMPT, text)
