"""Tests for PlaudClient initialization."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from plaud import PlaudClient


class TestPlaudClient:
    def test_init_with_explicit_token(self):
        client = PlaudClient(token="test-token")
        assert client._token == "test-token"
        assert client.recordings is not None
        assert client.transcriptions is not None
        assert client.speakers is not None
        assert client.tags is not None

    def test_init_from_env(self):
        with patch.dict(os.environ, {"PLAUD_TOKEN": "env-tok"}):
            client = PlaudClient()
            assert client._token == "env-tok"

    def test_init_raises_without_token(self):
        from pathlib import Path

        with patch.dict(os.environ, {}, clear=True), \
             patch("plaud.auth.ENV_FILE", Path("/nonexistent/.env")), \
             patch("plaud.auth.TOKEN_FILE", Path("/nonexistent/token")):
            os.environ.pop("PLAUD_TOKEN", None)
            with pytest.raises(ValueError, match="Plaud token not found"):
                PlaudClient()
