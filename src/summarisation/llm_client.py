import logging
from config.settings import settings
from src.summarisation.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.provider = (settings.SUMMARY_PROVIDER).lower()
        self.client = None

    def generate_summary(
        self, 
        prompt: str, 
        system_prompt: str = SYSTEM_PROMPT, 
        temperature: float = 0.2
    ) -> str:
        if self.provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                import importlib
                genai = importlib.import_module("google.generativeai")
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.GEMINI_MODEL)
                full_prompt = f"{system_prompt}\n\n{prompt}"
                response = model.generate_content(full_prompt)
                return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini LLM summary generation failed: {e}")
                raise e

        raise RuntimeError(
            f"Summary provider '{self.provider}' is not configured or unavailable"
        )
