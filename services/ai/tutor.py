"""AI tutor service (Phase 3 scaffolding).

This module intentionally provides minimal placeholder logic so Phase 3
endpoints can be wired without blocking on LLM/RAG integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant" | "system"
    content: str


async def build_tutor_context(
    *,
    exam_type: Optional[str],
    messages: List[ChatMessage],
) -> Dict[str, Any]:
    """Build retrieval/context payload for the tutor.

    Placeholder: real implementation will perform RAG retrieval based on
    exam_type and conversation history.
    """

    return {
        "exam_type": exam_type,
        "messages": [m.__dict__ for m in messages[-10:]],
        "retrieved": [],
    }


async def tutor_chat(
    *,
    exam_type: Optional[str],
    messages: List[ChatMessage],
) -> str:
    """Generate a tutor response.

    Placeholder response. Replace with LLM integration + RAG.
    """

    last_user = next((m for m in reversed(messages) if m.role == "user"), None)
    if not last_user:
        return "How can I help you with your exam preparation today?"

    return (
        "(AI Tutor placeholder) I received your message about your exam preparation. "
        f"Exam: {exam_type or 'unknown'}. "
        "Next: we will add RAG + LLM responses in Phase 3."
    )

