"""Tests for SpeakersAPI."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from plaud.api.speakers import SpeakersAPI
from plaud.exceptions import NotFoundError
from tests.conftest import SAMPLE_FILE_DETAIL, SAMPLE_SPEAKER


@pytest.fixture()
def api(mock_session: MagicMock) -> SpeakersAPI:
    return SpeakersAPI(mock_session)


class TestList:
    def test_returns_speakers(self, api: SpeakersAPI, mock_session: MagicMock):
        mock_session.get.return_value = {"data_speaker_list": [SAMPLE_SPEAKER]}
        speakers = api.list()
        assert len(speakers) == 1
        assert speakers[0].name == "Alice"
        assert speakers[0].id == "spk_001"


class TestRename:
    def test_renames_speaker_in_transcript(self, api: SpeakersAPI, mock_session: MagicMock):
        file_data = {
            **SAMPLE_FILE_DETAIL,
            "trans_result": [
                {"speaker": "Speaker 1", "content": "Hello", "start_time": 0, "end_time": 1000},
                {"speaker": "Speaker 2", "content": "Hi", "start_time": 1000, "end_time": 2000},
                {"speaker": "Speaker 1", "content": "Bye", "start_time": 2000, "end_time": 3000},
            ],
        }
        mock_session.post.return_value = {"data_file_list": [file_data]}
        mock_session.patch.return_value = {"data_file": {}}

        api.rename("abc123", "Speaker 1", "Alice")

        call_args = mock_session.patch.call_args
        segments = call_args.kwargs.get("json", call_args[1].get("json", {}))["trans_result"]
        speaker_names = [s["speaker"] for s in segments]
        assert speaker_names == ["Alice", "Speaker 2", "Alice"]

    def test_raises_if_speaker_not_in_recording(self, api: SpeakersAPI, mock_session: MagicMock):
        mock_session.post.return_value = {"data_file_list": [SAMPLE_FILE_DETAIL]}
        with pytest.raises(ValueError, match="not found in recording"):
            api.rename("abc123", "Nobody", "Alice")

    def test_raises_if_recording_not_found(self, api: SpeakersAPI, mock_session: MagicMock):
        mock_session.post.return_value = {"data_file_list": []}
        with pytest.raises(NotFoundError):
            api.rename("missing", "X", "Y")


class TestGetForRecording:
    def test_extracts_speakers(self, api: SpeakersAPI, mock_session: MagicMock):
        mock_session.post.return_value = {"data_file_list": [SAMPLE_FILE_DETAIL]}
        speakers = api.get_for_recording("abc123")
        names = {s["name"] for s in speakers}
        assert "Alice" in names
        assert "Bob" in names
