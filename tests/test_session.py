"""Tests for PlaudSession URL handling."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from plaud.session import PlaudSession


def _json_response(payload: dict):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = payload
    return resp


class TestPlaudSessionBaseUrl:
    def test_prefixes_relative_get_urls(self):
        session = PlaudSession("tok", base_url="https://api-apse1.plaud.ai/")
        response = _json_response({"ok": True})

        with patch.object(session._session, "get", return_value=response) as mock_get:
            assert session.get("/file/list") == {"ok": True}

        assert mock_get.call_args.args[0] == "https://api-apse1.plaud.ai/file/list"

    def test_leaves_absolute_get_urls_unchanged(self):
        session = PlaudSession("tok", base_url="https://api-apse1.plaud.ai")
        response = _json_response({"ok": True})

        with patch.object(session._session, "get", return_value=response) as mock_get:
            session.get("https://files.example.com/audio.mp3")

        assert mock_get.call_args.args[0] == "https://files.example.com/audio.mp3"

    def test_normalizes_trailing_slash(self):
        session = PlaudSession("tok", base_url="https://api-apse1.plaud.ai/")

        assert session.base_url == "https://api-apse1.plaud.ai"
