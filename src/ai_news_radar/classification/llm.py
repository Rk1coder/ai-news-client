import requests
from anthropic import Anthropic

from ai_news_radar.config import ANTHROPIC_API_KEY, CLASSIFIER_MODEL, GEMINI_API_KEY, GEMINI_MODEL, LLM_PROVIDER

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def call_llm(
    system_prompt: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    provider: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> str:
    """Hangi saglayici (Anthropic/Gemini) kullanilacaksa ona gore cagri yapar."""
    provider = (provider or LLM_PROVIDER).lower()
    if provider == "gemini":
        return _call_gemini(system_prompt, messages, max_tokens, api_key or GEMINI_API_KEY, model or GEMINI_MODEL)
    return _call_anthropic(system_prompt, messages, max_tokens, api_key or ANTHROPIC_API_KEY, model or CLASSIFIER_MODEL)


def _call_anthropic(system_prompt: str, messages: list[dict[str, str]], max_tokens: int, api_key: str, model: str) -> str:
    client = Anthropic(api_key=api_key)
    message = client.messages.create(model=model, max_tokens=max_tokens, system=system_prompt, messages=messages)
    return message.content[0].text.strip()


def _call_gemini(system_prompt: str, messages: list[dict[str, str]], max_tokens: int, api_key: str, model: str) -> str:
    contents = [
        {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
        for m in messages
    ]
    response = requests.post(
        GEMINI_URL.format(model=model),
        params={"key": api_key},
        json={
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
            # thinkingBudget 0: dusunme (reasoning) tokenlari max_tokens'i tuketip
            # gorunur cevabi bosaltabiliyor (finishReason=MAX_TOKENS, parts yok).
            "generationConfig": {"maxOutputTokens": max_tokens, "thinkingConfig": {"thinkingBudget": 0}},
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    candidate = data["candidates"][0]
    parts = candidate.get("content", {}).get("parts")
    if not parts:
        raise RuntimeError(f"Gemini yanit dondurmedi (finishReason={candidate.get('finishReason')})")
    return parts[0]["text"].strip()
