from unittest.mock import MagicMock, patch

from ai_news_radar.classification.llm import call_llm


@patch("ai_news_radar.classification.llm.Anthropic")
def test_call_llm_uses_anthropic_by_default(mock_anthropic):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(content=[MagicMock(text="cevap")])
    mock_anthropic.return_value = mock_client

    result = call_llm("sistem", [{"role": "user", "content": "soru"}], max_tokens=100)

    assert result == "cevap"
    mock_anthropic.assert_called_once()


@patch("ai_news_radar.classification.llm.requests.post")
def test_call_llm_dispatches_to_gemini(mock_post):
    mock_post.return_value = MagicMock(
        json=lambda: {"candidates": [{"content": {"parts": [{"text": "gemini cevabi"}]}}]},
        raise_for_status=lambda: None,
    )

    result = call_llm(
        "sistem", [{"role": "user", "content": "soru"}], max_tokens=100,
        provider="gemini", api_key="gemini-anahtari", model="gemini-2.5-flash",
    )

    assert result == "gemini cevabi"
    url, kwargs = mock_post.call_args
    assert "gemini-2.5-flash:generateContent" in url[0]
    assert kwargs["params"] == {"key": "gemini-anahtari"}
    assert kwargs["json"]["systemInstruction"]["parts"][0]["text"] == "sistem"
    assert kwargs["json"]["contents"] == [{"role": "user", "parts": [{"text": "soru"}]}]
    assert kwargs["json"]["generationConfig"]["thinkingConfig"] == {"thinkingBudget": 0}


@patch("ai_news_radar.classification.llm.requests.post")
def test_call_llm_raises_clear_error_when_gemini_returns_no_text(mock_post):
    mock_post.return_value = MagicMock(
        json=lambda: {"candidates": [{"content": {"role": "model"}, "finishReason": "MAX_TOKENS"}]},
        raise_for_status=lambda: None,
    )

    try:
        call_llm("sistem", [{"role": "user", "content": "soru"}], max_tokens=5, provider="gemini", api_key="k", model="m")
        raise AssertionError("beklenen RuntimeError firlatilmadi")
    except RuntimeError as exc:
        assert "MAX_TOKENS" in str(exc)


@patch("ai_news_radar.classification.llm.requests.post")
def test_call_llm_gemini_maps_assistant_role_to_model(mock_post):
    mock_post.return_value = MagicMock(
        json=lambda: {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]},
        raise_for_status=lambda: None,
    )

    call_llm(
        "sistem",
        [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}],
        max_tokens=100, provider="gemini", api_key="k", model="m",
    )

    contents = mock_post.call_args.kwargs["json"]["contents"]
    assert contents == [
        {"role": "user", "parts": [{"text": "a"}]},
        {"role": "model", "parts": [{"text": "b"}]},
    ]
