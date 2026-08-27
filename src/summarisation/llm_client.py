import logging
import ollama
from config.settings import settings
from src.summarisation.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.provider = (settings.SUMMARY_PROVIDER or "ollama").lower()
        self.ollama_host = settings.OLLAMA_HOST
        self.ollama_model = settings.OLLAMA_MODEL
        self.client = None
        
        if self.provider != "gemini":
            try:
                self.client = ollama.Client(host=self.ollama_host)
            except Exception as e:
                logger.warning(f"Failed to initialize Ollama client: {e}")

    def generate_summary(
        self, 
        prompt: str, 
        system_prompt: str = SYSTEM_PROMPT, 
        temperature: float = 0.2
    ) -> str:
        if self.provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel(settings.GEMINI_MODEL)
                full_prompt = f"{system_prompt}\n\n{prompt}"
                response = model.generate_content(full_prompt)
                return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini LLM summary generation failed: {e}")
                raise e

        if self.client is None:
            self.client = ollama.Client(host=self.ollama_host)

        try:
            kwargs = {
                "model": self.ollama_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "format": "json",
                "options": {
                    "temperature": temperature,
                    "num_predict": settings.summary_num_predict,
                }
            }
            if settings.summary_think is not None:
                kwargs["think"] = settings.summary_think

            response = self.client.chat(**kwargs)
            
            if isinstance(response, dict):
                return response["message"]["content"].strip()
            return response.message.content.strip()
        except Exception as e:
            logger.warning(f"Ollama summary generation error: {e}")
            raise e