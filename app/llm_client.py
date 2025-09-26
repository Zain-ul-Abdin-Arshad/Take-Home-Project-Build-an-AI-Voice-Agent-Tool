from __future__ import annotations

from typing import List, Dict, Optional
import httpx


class LLMClient:
    def generate(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    def generate(self, messages: List[Dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "messages": messages, "temperature": 0.6}
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()


class GeminiClient(LLMClient):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def generate(self, messages: List[Dict[str, str]]) -> str:
        # Convert OpenAI-style messages to Gemini prompt parts
        contents = []
        for m in messages:
            role = m.get("role", "user")
            text = m.get("content", "")
            if role == "system":
                # prepend as user content with instruction tag
                contents.append({"role": "user", "parts": [{"text": f"[SYSTEM]\n{text}"}]})
            elif role == "assistant":
                contents.append({"role": "model", "parts": [{"text": text}]})
            else:
                contents.append({"role": "user", "parts": [{"text": text}]})

        params = {"temperature": 0.6}
        payload = {"contents": contents, "generationConfig": params}
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{self.base_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates") or []
            if not candidates:
                return ""
            parts = (candidates[0].get("content") or {}).get("parts") or []
            if parts and "text" in parts[0]:
                return parts[0]["text"].strip()
            return ""


def build_messages(system_prompt: str, turns: List[Dict[str, str]], user_utterance: str) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    for t in turns:
        messages.append({"role": "user", "content": t["user"]})
        messages.append({"role": "assistant", "content": t["assistant"]})
    messages.append({"role": "user", "content": user_utterance})
    return messages


