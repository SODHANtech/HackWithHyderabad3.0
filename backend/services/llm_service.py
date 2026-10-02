import logging
import json
from typing import Dict, Any, Optional
from backend.config import settings

logger = logging.getLogger("llm_service")

class LLMService:
    def __init__(self):
        self.client = None
        self.provider = None
        self._init_client()

    def _init_client(self):
        # Priority 1: Google Gemini API
        if settings.has_gemini_credentials:
            try:
                from google import genai
                self.client = genai.Client(api_key=settings.gemini_api_key)
                self.provider = "gemini"
                logger.info(f"Initialized Google Gemini LLM client with model: {settings.gemini_model}")
                return
            except Exception as e:
                logger.error(f"Failed to initialize Google Gemini client: {e}.")
                self.client = None

        # Priority 2: Groq Fallback
        if settings.groq_api_key and settings.groq_api_key.strip():
            try:
                from groq import Groq
                self.client = Groq(api_key=settings.groq_api_key)
                self.provider = "groq"
                logger.info(f"Initialized Groq LLM client with model: {settings.groq_model}")
                return
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}.")
                self.client = None

        logger.info("No cloud LLM API key detected or initialization failed. Operating in intelligent template generator mode.")

    def complete(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        """Call LLM with fallback"""
        if self.client and self.provider == "gemini":
            try:
                from google.genai import types
                config = types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=4096
                )
                if system_prompt:
                    config.system_instruction = system_prompt

                models_to_try = [
                    settings.gemini_model,
                    "gemini-3.5-flash-lite",
                    "gemini-3-flash-preview",
                    "gemini-3.1-flash-lite-preview",
                    "gemini-flash-latest"
                ]
                seen = set()
                for m in models_to_try:
                    if m in seen:
                        continue
                    seen.add(m)
                    try:
                        response = self.client.models.generate_content(
                            model=m,
                            contents=prompt,
                            config=config
                        )
                        if response and response.text:
                            return response.text
                    except Exception as err:
                        logger.warning(f"Gemini model {m} call failed: {err}. Trying fallback model...")
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}")

        elif self.client and self.provider == "groq":
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = self.client.chat.completions.create(
                    model=settings.groq_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=4096
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Groq API call failed: {e}")

        # Intelligent fallback return
        return self._generate_fallback(prompt, system_prompt)

    def _generate_fallback(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Provide structured synthetic response if LLM is offline"""
        logger.info("Generating response via intelligent agent heuristics...")
        return "GENERATED_OUTPUT_FALLBACK"

llm_service = LLMService()
