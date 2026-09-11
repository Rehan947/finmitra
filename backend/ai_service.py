"""AI Service integration for FinMitra using the official google-genai SDK."""

import os
import logging
from typing import List, Optional
from dotenv import load_dotenv

from backend.prompt import SYSTEM_PROMPT
from backend.schemas import ChatMessageItem

# Load environment variables
load_dotenv()

logger = logging.getLogger("finmitra.ai")
logger.setLevel(logging.INFO)

# Primary and fallback model configurations
DEFAULT_PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
FALLBACK_MODEL = "gemini-3.5-flash-lite"


class AIServiceError(Exception):
    """Custom exception for AI service issues with user-facing messages."""
    def __init__(self, message: str, status_code: int = 500, error_code: str = "AI_ERROR"):
        super().__init__(message)
        self.user_message = message
        self.status_code = status_code
        self.error_code = error_code


class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.primary_model = DEFAULT_PRIMARY_MODEL
        self.client = None
        self.status = "not_configured" if not self.api_key else "configured"
        self.last_error_reason = None
        self._initialize_client()

    def _initialize_client(self):
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set in environment.")
            self.client = None
            self.status = "not_configured"
            return

        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.status = "configured"
            logger.info("Google GenAI client successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize GenAI client: {type(e).__name__}")
            self.client = None
            self.status = "unavailable"
            self.last_error_reason = f"Initialization error: {type(e).__name__}"

    def is_ready(self) -> bool:
        return self.client is not None and bool(self.api_key)

    def get_health_status(self) -> dict:
        return {
            "status": self.status,
            "configured": bool(self.api_key),
            "primary_model": self.primary_model,
            "fallback_model": FALLBACK_MODEL,
            "error_reason": self.last_error_reason
        }

    async def generate_chat_response(
        self,
        message: str,
        conversation_history: Optional[List[ChatMessageItem]] = None
    ) -> str:
        """Generates an AI response for a user financial query with safety rules and SDG 1 focus."""
        if not self.is_ready():
            raise AIServiceError(
                "The AI service is not configured with a valid API key. Please check server settings.",
                status_code=503,
                error_code="API_KEY_MISSING"
            )

        from google.genai import types
        from google.genai.errors import APIError, ClientError

        # Build contents
        contents = []
        if conversation_history:
            # Include up to the last 4 messages for context and token efficiency
            recent_history = conversation_history[-4:]
            for item in recent_history:
                role = "user" if item.role.lower() == "user" else "model"
                # Bound past message tokens so they don't consume prompt budget
                text_content = item.content if len(item.content) <= 500 else item.content[:500] + "..."
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=text_content)]
                    )
                )

        # Append current user prompt
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=message)]
            )
        )

        # Try primary model first, fallback to fallback model if needed
        models_to_try = [self.primary_model]
        if FALLBACK_MODEL != self.primary_model:
            models_to_try.append(FALLBACK_MODEL)

        last_error = None

        for model_name in models_to_try:
            try:
                # Build model-specific config (lite models do not support thinking_config)
                if "lite" in model_name.lower():
                    config = types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.6,
                        max_output_tokens=2048
                    )
                else:
                    config = types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.6,
                        max_output_tokens=2048,
                        thinking_config=types.ThinkingConfig(thinking_budget=0)
                    )

                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config
                )

                if response and response.text:
                    resp_text = response.text.strip()
                    
                    # Update status to reachable
                    self.status = "provider_reachable"
                    self.last_error_reason = None

                    # Inspect finish reason
                    finish_reason = None
                    if response.candidates:
                        finish_reason = getattr(response.candidates[0], "finish_reason", None)
                    
                    finish_str = str(finish_reason).upper() if finish_reason else ""
                    if "MAX_TOKENS" in finish_str:
                        logger.warning(f"Response reached MAX_TOKENS on {model_name}.")
                        if not resp_text.endswith((".", "?", "!", "**", "*")):
                            resp_text += "...\n\n*(Note: To keep answers practical and within reading limits, FinMitra concluded here. Feel free to ask me to expand further!)*"

                    return resp_text
                else:
                    raise AIServiceError(
                        "FinMitra was unable to generate a response for this query. Please try rephrasing.",
                        status_code=502,
                        error_code="EMPTY_RESPONSE"
                    )

            except (ClientError, APIError) as e:
                err_str = str(e).lower()
                logger.warning(f"Gemini API error on {model_name}: {type(e).__name__} (code: {getattr(e, 'code', 'N/A')})")

                # Handle Quota / Rate Limit: try fallback model first
                if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str or "rate limit" in err_str:
                    if model_name != models_to_try[-1]:
                        logger.warning(f"Rate limited on {model_name}. Attempting fallback model...")
                        last_error = e
                        continue
                    self.status = "quota_limited"
                    self.last_error_reason = "Usage or quota limit reached"
                    raise AIServiceError(
                        "FinMitra is temporarily receiving high traffic or has reached usage limits. Please wait a moment and try again.",
                        status_code=429,
                        error_code="RATE_LIMIT_OR_QUOTA"
                    )

                # If 404 model not found, try fallback
                if "404" in err_str or "not found" in err_str:
                    last_error = e
                    continue

                # Authentication error
                if "401" in err_str or "403" in err_str or "api_key_invalid" in err_str or "unauthenticated" in err_str:
                    self.status = "authentication_failed"
                    self.last_error_reason = "Authentication failed (invalid or revoked API key)"
                    raise AIServiceError(
                        "AI service authentication failed. Please verify API key permissions.",
                        status_code=401,
                        error_code="AUTH_FAILED"
                    )

                last_error = e

            except Exception as e:
                logger.error(f"Unexpected error calling Gemini ({model_name}): {type(e).__name__}")
                last_error = e

        # If all model attempts failed
        err_msg = str(last_error).lower() if last_error else ""
        if "timeout" in err_msg or "timed out" in err_msg or "connection" in err_msg:
            self.status = "unavailable"
            self.last_error_reason = "Timeout or connection issue"
            raise AIServiceError(
                "FinMitra could not reach the AI service right now. Please check your connection and retry.",
                status_code=504,
                error_code="TIMEOUT"
            )

        self.status = "unavailable"
        self.last_error_reason = str(last_error)
        raise AIServiceError(
            "FinMitra encountered a temporary error processing your request. Please try again in a moment.",
            status_code=500,
            error_code="INTERNAL_AI_ERROR"
        )


# Global singleton instance
ai_service = AIService()
