from unittest.mock import patch, MagicMock
import app.services.namegen as n


def _mock_openai(content: str):
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    client = MagicMock()
    client.chat.completions.create.return_value = resp
    return client


def test_brainstorm_no_api_key(monkeypatch):
    monkeypatch.setattr(n.settings, "OPENAI_API_KEY", None)
    assert n.brainstorm(["ai"], "tech") == []


def test_brainstorm_returns_valid_domains(monkeypatch):
    monkeypatch.setattr(n.settings, "OPENAI_API_KEY", "sk-test")
    body = "aifast.com\nquickbot.io\nnot-a-domain\nspeedai.ai\n"
    with patch("app.services.namegen.OpenAI", return_value=_mock_openai(body)):
        result = n.brainstorm(["ai", "fast"], "tech")
    assert "aifast.com" in result
    assert "quickbot.io" in result
    assert "speedai.ai" in result
    assert "not-a-domain" not in result


def test_brainstorm_strips_bullets(monkeypatch):
    monkeypatch.setattr(n.settings, "OPENAI_API_KEY", "sk-test")
    body = "• aifast.com\n- quickbot.io\n– speedai.ai\n"
    with patch("app.services.namegen.OpenAI", return_value=_mock_openai(body)):
        result = n.brainstorm(["ai"], "tech")
    assert "aifast.com" in result
    assert "quickbot.io" in result
    assert "speedai.ai" in result


def test_brainstorm_respects_count_limit(monkeypatch):
    monkeypatch.setattr(n.settings, "OPENAI_API_KEY", "sk-test")
    body = "\n".join(f"domain{i}.com" for i in range(20))
    with patch("app.services.namegen.OpenAI", return_value=_mock_openai(body)):
        result = n.brainstorm(["x"], "niche", count=5)
    assert len(result) == 5


def test_brainstorm_openai_error_returns_empty(monkeypatch):
    monkeypatch.setattr(n.settings, "OPENAI_API_KEY", "sk-test")
    client = MagicMock()
    client.chat.completions.create.side_effect = Exception("API error")
    with patch("app.services.namegen.OpenAI", return_value=client):
        assert n.brainstorm(["ai"], "tech") == []
