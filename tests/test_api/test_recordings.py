"""Tests for RecordingsAPI."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from plaud.api.recordings import RecordingsAPI
from plaud.exceptions import NotFoundError
from tests.conftest import SAMPLE_FILE_DETAIL, SAMPLE_FILE_SIMPLE


@pytest.fixture()
def api(mock_session: MagicMock) -> RecordingsAPI:
    return RecordingsAPI(mock_session)


class TestList:
    def test_returns_recordings(self, api: RecordingsAPI, mock_session: MagicMock):
        mock_session.get.return_value = {"data_file_list": [SAMPLE_FILE_SIMPLE]}
        result = api.list(limit=10)
        assert len(result) == 1
        assert result[0].id == "abc123"
        assert result[0].filename == "Team Standup"

    def test_empty_list(self, api: RecordingsAPI, mock_session: MagicMock):
        mock_session.get.return_value = {"data_file_list": []}
        assert api.list() == []


class TestGet:
    def test_returns_recording(self, api: RecordingsAPI, mock_session: MagicMock):
        mock_session.post.return_value = {"data_file_list": [SAMPLE_FILE_DETAIL]}
        r = api.get("abc123")
        assert r.id == "abc123"

    def test_not_found(self, api: RecordingsAPI, mock_session: MagicMock):
        mock_session.post.return_value = {"data_file_list": []}
        with pytest.raises(NotFoundError):
            api.get("missing")


class TestGetAudioUrl:
    def test_returns_url(self, api: RecordingsAPI, mock_session: MagicMock):
        mock_session.get.return_value = {"temp_url": "https://s3.example.com/audio.mp3"}
        assert api.get_audio_url("abc123") == "https://s3.example.com/audio.mp3"
