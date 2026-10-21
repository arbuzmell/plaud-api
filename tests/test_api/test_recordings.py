"""Tests for RecordingsAPI."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from plaud.api.recordings import UPLOAD_PART_SIZE, RecordingsAPI
from plaud.exceptions import NotFoundError, UploadError
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


class TestUpload:
    @staticmethod
    def _setup(mock_session: MagicMock, n_parts: int) -> None:
        mock_session.post.side_effect = [
            {"data": {
                "part_urls": [f"https://s3.example.com/part{i}" for i in range(1, n_parts + 1)],
                "upload_id": "up1",
                "object_name": "obj1",
            }},
            {},  # merge
            {"data": SAMPLE_FILE_SIMPLE},  # confirm
        ]
        mock_session.put_raw.side_effect = [
            MagicMock(status_code=200, headers={"ETag": f'"etag{i}"'})
            for i in range(1, n_parts + 1)
        ]

    def test_small_file_single_part(self, api, mock_session, tmp_path):
        f = tmp_path / "a.mp3"
        f.write_bytes(b"x" * 1000)
        self._setup(mock_session, 1)
        rec = api.upload(f, name="Standup")
        assert rec.id == "abc123"
        assert mock_session.put_raw.call_args.kwargs["data"] == b"x" * 1000
        merge = mock_session.post.call_args_list[1].kwargs["json"]
        assert merge["parts"] == [{"Etag": "etag1", "PartNumber": 1}]

    def test_large_file_uploads_every_part(self, api, mock_session, tmp_path):
        size = 2 * UPLOAD_PART_SIZE + 123
        f = tmp_path / "meeting.mp3"
        f.write_bytes(bytes(range(256)) * (size // 256) + b"\x00" * (size % 256))
        self._setup(mock_session, 3)
        api.upload(f, name="Meeting")
        sent = [c.kwargs["data"] for c in mock_session.put_raw.call_args_list]
        assert [len(b) for b in sent] == [UPLOAD_PART_SIZE, UPLOAD_PART_SIZE, 123]
        assert b"".join(sent) == f.read_bytes()
        assert [c.args[0] for c in mock_session.put_raw.call_args_list] == [
            "https://s3.example.com/part1",
            "https://s3.example.com/part2",
            "https://s3.example.com/part3",
        ]
        merge = mock_session.post.call_args_list[1].kwargs["json"]
        assert merge["parts"] == [
            {"Etag": "etag1", "PartNumber": 1},
            {"Etag": "etag2", "PartNumber": 2},
            {"Etag": "etag3", "PartNumber": 3},
        ]

    def test_part_count_mismatch_raises(self, api, mock_session, tmp_path):
        f = tmp_path / "meeting.mp3"
        f.write_bytes(b"x" * (UPLOAD_PART_SIZE + 1))
        self._setup(mock_session, 1)
        with pytest.raises(UploadError, match="Expected 2 upload part URLs"):
            api.upload(f)
        mock_session.put_raw.assert_not_called()

    def test_failed_part_raises(self, api, mock_session, tmp_path):
        f = tmp_path / "a.mp3"
        f.write_bytes(b"x" * 10)
        self._setup(mock_session, 1)
        mock_session.put_raw.side_effect = [MagicMock(status_code=403, text="denied", headers={})]
        with pytest.raises(UploadError, match="part 1/1 failed: 403"):
            api.upload(f)

    def test_start_time_sets_recording_date(self, api, mock_session, tmp_path):
        f = tmp_path / "a.mp3"
        f.write_bytes(b"x" * 10)
        self._setup(mock_session, 1)
        started = datetime(2026, 10, 20, 16, 58, tzinfo=timezone.utc)
        api.upload(f, start_time=started)
        confirm = mock_session.post.call_args_list[2].kwargs["json"]
        assert confirm["start_time"] == 1792515480000
        assert confirm["session_id"] == 1792515480
