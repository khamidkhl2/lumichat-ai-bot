import logging
from typing import List, Dict, Optional, Any
import aiohttp
from config import config

logger = logging.getLogger(__name__)

# Try importing groq library
try:
    from groq import AsyncGroq
    HAS_GROQ_SDK = True
except ImportError:
    HAS_GROQ_SDK = False

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

class GroqService:
    def __init__(self):
        self.api_key = config.GROQ_API_KEY
        self.primary_model = config.GROQ_PRIMARY_MODEL
        self.fallback_model = config.GROQ_FALLBACK_MODEL
        self.client: Optional[Any] = None
        if HAS_GROQ_SDK and self.api_key:
            self.client = AsyncGroq(api_key=self.api_key)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        user_lang: str = "en"
    ) -> str:
        """
        Sends conversation history + system prompt to Groq API.
        Attempts primary model first, falling back to secondary model if needed.
        """
        if not self.api_key:
            logger.warning("GROQ_API_KEY is not configured!")
            return (
                "⚠️ <b>Groq API Key is not set!</b>\n\n"
                "Please configure <code>GROQ_API_KEY</code> in your <code>.env</code> file. "
                "You can get a 100% free API key from https://console.groq.com."
            )

        # Build full payload with system prompt at top
        payload_messages = [{"role": "system", "content": system_prompt}]
        payload_messages.extend(messages)

        # 1. Try with primary model
        try:
            return await self._call_model(self.primary_model, payload_messages)
        except Exception as e:
            logger.warning(f"Groq primary model '{self.primary_model}' failed: {e}. Trying fallback '{self.fallback_model}'...")
            try:
                return await self._call_model(self.fallback_model, payload_messages)
            except Exception as e2:
                logger.error(f"Groq fallback model '{self.fallback_model}' also failed: {e2}")
                return (
                    "⚠️ <i>Sorry, our AI engine is currently experiencing high load. "
                    "Please wait a moment and send your message again!</i>"
                )

    async def _call_model(self, model: str, messages: List[Dict[str, str]]) -> str:
        # Prefer AsyncGroq SDK if initialized
        if self.client:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=config.GROQ_TEMPERATURE,
                max_tokens=config.GROQ_MAX_TOKENS,
            )
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content or ""
            return ""
        
        # Fallback to direct aiohttp call
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": config.GROQ_TEMPERATURE,
            "max_tokens": config.GROQ_MAX_TOKENS
        }
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=45)) as session:
            async with session.post(GROQ_ENDPOINT, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    err_body = await resp.text()
                    raise RuntimeError(f"Groq API error HTTP {resp.status}: {err_body}")
                data = await resp.json()
                return data["choices"][0]["message"]["content"]

groq_service = GroqService()
