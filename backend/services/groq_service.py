import os
import json
import logging
from typing import Dict, Any
import httpx

from backend.config import settings

logger = logging.getLogger("groq_service")

class GroqService:
    """Wrapper around Groq LLM to fetch structured business data from a natural language prompt."""

    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model or "qwen/qwen3.8-27b"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    async def get_business_profile(self, prompt: str) -> Dict[str, Any]:
        """Ask Groq to generate a structured JSON with business details.
        The prompt should ask for fields: name, category, location, phone, whatsapp,
        assets (logo_url, photos, video_url, brochure_url, pricing_tiers).
        Returns a dict parsed from the LLM response with resilient fallback.
        """
        if not self.api_key:
            return self._fallback_profile(prompt)
        
        system_prompt = (
            "You are an expert JSON generator. Given a user description, output a JSON object "
            "with the following keys: name (string), category (string), location (string), "
            "phone (string), whatsapp (string, may be same as phone), assets (object) containing "
            "logo_url (string, optional), photos (list of objects with url, title, desc), "
            "video_url (string, optional), brochure_url (string, optional), pricing_tiers "
            "(list of objects with name, price, period, badge, features)."
            "Only output the JSON without any surrounding text."
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1024,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            cleaned = content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            business_data = json.loads(cleaned.strip())
            if isinstance(business_data, dict):
                return business_data
        except Exception as e:
            logger.warning(f"Groq API call or JSON decode failed: {e}. Using resilient fallback profile.")
        
        return self._fallback_profile(prompt)

    def _fallback_profile(self, prompt: str) -> Dict[str, Any]:
        words = prompt.split()
        name = " ".join(words[:3]).title() if len(words) >= 3 else (prompt.title() or "Local Enterprise")
        return {
            "name": name,
            "category": "Local Business",
            "location": "Metro Area",
            "phone": "+1 555-0100",
            "whatsapp": "+1 555-0100",
            "services": prompt,
            "assets": {}
        }
