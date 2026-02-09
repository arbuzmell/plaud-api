"""Tests for plaud.auth module."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from plaud.auth import clear_token, resolve_token, save_token


class TestResolveToken:
    def test_explicit_token(self):
        assert resolve_token("my-token") == "my-token"

    def test_env_var(self):
        with patch.dict(os.environ, {"PLAUD_TOKEN": "env-token"}):
            assert resolve_token() == "env-token"

    def test_dotenv_token(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("PLAUD_TOKEN=dotenv-token\n")

        with patch("plaud.auth.ENV_FILE", env_file), \
             patch("plaud.auth.TOKEN_FILE", Path("/nonexistent/token")), \
             patch.dict(os.environ, {}, clear=True):
            os.environ.pop("PLAUD_TOKEN", None)
            assert resolve_token() == "dotenv-token"

    def test_dotenv_quoted(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text('PLAUD_TOKEN="quoted-token"\n')

        with patch("plaud.auth.ENV_FILE", env_file), \
             patch("plaud.auth.TOKEN_FILE", Path("/nonexistent/token")), \
             patch.dict(os.environ, {}, clear=True):
            os.environ.pop("PLAUD_TOKEN", None)
            assert resolve_token() == "quoted-token"

    def test_file_token(self, tmp_path: Path):
        token_file = tmp_path / "token"
        token_file.write_text("file-token\n")

        with patch("plaud.auth.TOKEN_FILE", token_file), \
             patch("plaud.auth.ENV_FILE", Path("/nonexistent/.env")), \
             patch.dict(os.environ, {}, clear=True):
            os.environ.pop("PLAUD_TOKEN", None)
            assert resolve_token() == "file-token"

    def test_explicit_takes_priority(self):
        with patch.dict(os.environ, {"PLAUD_TOKEN": "env-token"}):
            assert resolve_token("explicit") == "explicit"

    def test_env_takes_priority_over_dotenv(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("PLAUD_TOKEN=dotenv-token\n")

        with patch("plaud.auth.ENV_FILE", env_file), \
             patch.dict(os.environ, {"PLAUD_TOKEN": "env-token"}):
            assert resolve_token() == "env-token"

    def test_raises_when_nothing_found(self):
        with patch.dict(os.environ, {}, clear=True), \
             patch("plaud.auth.ENV_FILE", Path("/nonexistent/.env")), \
             patch("plaud.auth.TOKEN_FILE", Path("/nonexistent/token")):
            os.environ.pop("PLAUD_TOKEN", None)
            with pytest.raises(ValueError, match="Plaud token not found"):
                resolve_token()


class TestSaveToken:
    def test_saves_to_dotenv(self, tmp_path: Path):
        env_file = tmp_path / ".env"

        with patch("plaud.auth.ENV_FILE", env_file):
            path = save_token("saved-token")
            assert path == env_file.resolve()
            assert "PLAUD_TOKEN=saved-token" in env_file.read_text()

    def test_updates_existing_dotenv(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("OTHER_VAR=hello\nPLAUD_TOKEN=old-token\n")

        with patch("plaud.auth.ENV_FILE", env_file):
            save_token("new-token")
            content = env_file.read_text()
            assert "PLAUD_TOKEN=new-token" in content
            assert "OTHER_VAR=hello" in content
            assert "old-token" not in content


class TestClearToken:
    def test_removes_from_dotenv(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("OTHER=keep\nPLAUD_TOKEN=remove-me\n")

        with patch("plaud.auth.ENV_FILE", env_file), \
             patch("plaud.auth.TOKEN_FILE", Path("/nonexistent/token")):
            clear_token()
            content = env_file.read_text()
            assert "PLAUD_TOKEN" not in content
            assert "OTHER=keep" in content

    def test_deletes_dotenv_if_only_token(self, tmp_path: Path):
        env_file = tmp_path / ".env"
        env_file.write_text("PLAUD_TOKEN=remove-me\n")

        with patch("plaud.auth.ENV_FILE", env_file), \
             patch("plaud.auth.TOKEN_FILE", Path("/nonexistent/token")):
            clear_token()
            assert not env_file.exists()

    def test_removes_global_config(self, tmp_path: Path):
        token_file = tmp_path / "token"
        token_file.write_text("token")

        with patch("plaud.auth.ENV_FILE", Path("/nonexistent/.env")), \
             patch("plaud.auth.TOKEN_FILE", token_file):
            clear_token()
            assert not token_file.exists()

    def test_noop_if_nothing(self, tmp_path: Path):
        with patch("plaud.auth.ENV_FILE", Path("/nonexistent/.env")), \
             patch("plaud.auth.TOKEN_FILE", tmp_path / "nonexistent"):
            clear_token()  # should not raise
