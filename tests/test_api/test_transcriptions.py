"""Tests for TranscriptionsAPI."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from plaud.api.transcriptions import TranscriptionsAPI
from plaud.exceptions import AnalysisTimeoutError
from tests.conftest import (
    SAMPLE_ANALYSIS_COMPLETE,
    SAMPLE_ANALYSIS_PROCESSING,
    SAMPLE_FILE_DETAIL,
)


@pytest.fixture()
def api(mock_session: MagicMock) -> TranscriptionsAPI:
    return TranscriptionsAPI(mock_session)


class TestGetStatus:
    def test_complete(self, api: TranscriptionsAPI, mock_session: MagicMock):
        mock_session.post.return_value = SAMPLE_ANALYSIS_COMPLETE
        status = api.get_status("abc123")
        assert status.complete is True

    def test_processing(self, api: TranscriptionsAPI, mock_session: MagicMock):
        mock_session.post.return_value = SAMPLE_ANALYSIS_PROCESSING
        status = api.get_status("abc123")
        assert status.complete is False


class TestGet:
    def test_returns_transcription(self, api: TranscriptionsAPI, mock_session: MagicMock):
        mock_session.post.return_value = {"data_file_list": [SAMPLE_FILE_DETAIL]}
        t = api.get("abc123")
        assert t.recording_id == "abc123"
        assert len(t.segments) == 2
        assert t.segments[0].speaker == "Alice"
        assert t.segments[0].text == "Good morning everyone."


class TestGetSummary:
    def test_returns_summary(self, api: TranscriptionsAPI, mock_session: MagicMock):
        mock_session.post.return_value = {"data_file_list": [SAMPLE_FILE_DETAIL]}
        s = api.get_summary("abc123")
        assert "Meeting Summary" in s.content


class TestWait:
    def test_timeout_raises(self, api: TranscriptionsAPI, mock_session: MagicMock):
        mock_session.post.return_value = SAMPLE_ANALYSIS_PROCESSING
        with pytest.raises(AnalysisTimeoutError):
            api.wait("abc123", timeout=0, poll_interval=0)
