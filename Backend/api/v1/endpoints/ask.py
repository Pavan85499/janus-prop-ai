"""
Ask Janus AI endpoints backed by Gemini.

Provides a simple chat endpoint that forwards prompts to the Gemini agent and
returns a text response. Falls back gracefully when Gemini is not configured.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

try:
    from agents.gemini_ai_agent import get_gemini_agent
except ImportError:
    get_gemini_agent = None


router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None
    property_data: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    reply: str
    model: str = "gemini"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


@router.post("/chat", response_model=ChatResponse)
async def chat_with_janus(body: ChatRequest) -> ChatResponse:
    """Forward a user message to the Gemini agent and return its reply."""
    try:
        if not get_gemini_agent:
            raise HTTPException(status_code=500, detail="Gemini agent unavailable")
        agent = get_gemini_agent()
        if not getattr(agent, "is_initialized", False):
            # Return graceful message when not configured
            return ChatResponse(
                reply=(
                    "Gemini is not configured. Please set GEMINI_API_KEY in the backend environment "
                    "to enable AI responses."
                )
            )

        # Build a prompt using optional context
        context_str = "" if not body.context else f"\nContext: {body.context}"
        prop_str = "" if not body.property_data else f"\nProperty: {body.property_data}"
        prompt = f"User: {body.message}{context_str}{prop_str}\nAssistant:"

        # Use the agent's internal generator
        try:
            reply_text = await agent._generate_response(prompt)
            return ChatResponse(reply=reply_text)
        except Exception as gen_err:
            msg = str(gen_err)
            # Graceful handling for common Gemini key/config errors
            if (
                "API key" in msg or
                "API_KEY_INVALID" in msg or
                "expired" in msg or
                "permission" in msg.lower()
            ):
                return ChatResponse(
                    reply=(
                        "Gemini API key is invalid or expired. Please set/renew GEMINI_API_KEY in the backend "
                        "environment and restart the server."
                    )
                )
            # Unknown generation failure
            raise HTTPException(status_code=500, detail=f"Chat failed: {msg}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


