"""
LLM client for the AI assistant, wrapping the Groq API.
"""

import time

import groq
from groq import Groq
from django.conf import settings


class LLMUnavailableError(Exception):
    pass


class LLMClient:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def chat(self, messages: list[dict], temperature: float = 0.7) -> str:
        """Send a list of {role, content} messages and return the assistant reply."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                timeout=settings.GROQ_TIMEOUT,
            )
            return response.choices[0].message.content
        except (groq.APITimeoutError, groq.APIConnectionError):
            raise LLMUnavailableError(
                "The AI assistant is temporarily unavailable. Please try again later."
            )
        except groq.RateLimitError:
            time.sleep(5)
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    timeout=settings.GROQ_TIMEOUT,
                )
                return response.choices[0].message.content
            except groq.RateLimitError:
                raise LLMUnavailableError(
                    "The AI assistant is temporarily unavailable. Please try again later."
                )
