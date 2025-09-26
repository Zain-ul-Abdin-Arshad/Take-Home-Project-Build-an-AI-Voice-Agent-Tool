from __future__ import annotations

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from .llm_client import LLMClient, build_messages


@dataclass
class ConversationContext:
    system_prompt: str
    settings: Dict[str, Any]
    call_id: Optional[str] = None
    load_number: Optional[str] = None
    driver_name: Optional[str] = None
    turns: List[Dict[str, str]] = field(default_factory=list)


def build_system_prompt(base_prompt: str, ctx: ConversationContext) -> str:
    behavior = ctx.settings.get("conversation_flow", {})
    emergency_keywords = behavior.get("emergency_keywords", [])
    status_keywords = behavior.get("status_keywords", [])

    instructions = (
        "You are an AI voice agent for a logistics dispatch team. "
        "Always be concise, helpful, and professional. "
        "Use open-ended questions first, then focused follow-ups. "
        "If the driver speaks one-word answers repeatedly, proactively probe 2-3 times, then end the call politely. "
        "If the audio is noisy or unclear, ask to repeat up to 2 times, then end the call and promise a call back. "
        "If an emergency is detected, immediately gather location, nature of emergency, and safety status, then end the call stating a dispatcher will call back."
    )

    keywords_block = (
        f"Emergency keywords to watch for: {', '.join(emergency_keywords)}. "
        f"Status keywords include: {', '.join(status_keywords)}. "
    )

    context_block = (
        f"Driver name: {ctx.driver_name or 'Unknown'}. "
        f"Load number: {ctx.load_number or 'Unknown'}. "
    )

    return f"{base_prompt}\n\n{instructions}\n\n{keywords_block}{context_block}"


def generate_reply(llm: LLMClient, ctx: ConversationContext, user_text: str) -> str:
    messages = build_messages(ctx.system_prompt, ctx.turns, user_text)
    reply = llm.generate(messages)
    ctx.turns.append({"user": user_text, "assistant": reply})
    return reply


