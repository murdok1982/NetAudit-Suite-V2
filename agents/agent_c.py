from .base_agent import BaseAgent

class StrategyAgent(BaseAgent):
    PROMPT = """
    Eres un experto en ciberinteligencia (OSINT/SOCMINT).
    Consolida los análisis de psicología forense y de inteligencia junto con los datos técnicos.
    Diseña un informe de inteligencia ejecutivo con conclusiones, TTPs y recomendaciones operativas defensivas.
    Output: JSON consolidado para el reporte final.
    """

    def analyze(self, analyses_text: str) -> str:
        return self._call_llm(self.PROMPT, analyses_text)
