"""Tests for PlaudSession URL handling."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from plaud.exceptions import APIError
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


class TestPlaudSessionPutRaw:
    def test_put_raw_does_not_send_bearer_authorization_to_s3(self):
        session = PlaudSession("secret-token")
        response = MagicMock()

        with patch("plaud.session.requests.put", return_value=response) as mock_put:
            result = session.put_raw(
                "https://s3.example.com/presigned",
                data=b"abc",
                headers={"Content-Type": "application/octet-stream"},
            )

        assert result is response
        assert mock_put.call_args.args[0] == "https://s3.example.com/presigned"
        assert mock_put.call_args.kwargs["headers"] == {
            "Content-Type": "application/octet-stream"
        }
        assert "Authorization" not in mock_put.call_args.kwargs["headers"]


class TestPlaudSessionHandle:
    def test_region_mismatch_payload_raises_api_error(self):
        response = MagicMock()
        response.status_code = 200
        response.text = '{"status": -302, "msg": "user region mismatch"}'
        response.json.return_value = {"status": -302, "msg": "user region mismatch"}

        with pytest.raises(APIError, match="user region mismatch"):
            PlaudSession._handle(response)
