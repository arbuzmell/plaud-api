"""Tests for plaud.models."""

from __future__ import annotations

from plaud.models import (
    AnalysisStatus,
    Recording,
    Summary,
    Tag,
    TranscriptionSegment,
)


class TestRecording:
    def test_from_api_response(self):
        r = Recording.model_validate({
            "id": "abc",
            "filename": "Test",
            "duration": 65000,
            "filesize": 1024,
            "start_time": 1700000000000,
            "is_trans": 1,
            "is_summary": 0,
            "filetag_id_list": ["t1"],
        })
        assert r.id == "abc"
        assert r.filename == "Test"
        assert r.duration_ms == 65000
        assert r.has_transcription is True
        assert r.has_summary is False
        assert r.tag_ids == ["t1"]
        assert r.duration_display == "1:05"

    def test_duration_seconds(self):
        r = Recording(id="x", duration_ms=90500)
        assert r.duration_seconds == 90.5


class TestTranscriptionSegment:
    def test_from_api(self):
        seg = TranscriptionSegment.model_validate({
            "speaker": "Alice",
            "content": "Hello",
            "start_time": 1000,
            "end_time": 3000,
        })
        assert seg.speaker == "Alice"
        assert seg.text == "Hello"
        assert seg.start_time_ms == 1000
        assert seg.end_time_ms == 3000


class TestSummary:
    def test_parse_ai_content_plain(self):
        assert Summary.parse_ai_content("plain text") == "plain text"

    def test_parse_ai_content_json_markdown(self):
        raw = '{"markdown": "# Summary"}'
        assert Summary.parse_ai_content(raw) == "# Summary"

    def test_parse_ai_content_json_nested(self):
        raw = '{"content": {"markdown": "nested"}}'
        assert Summary.parse_ai_content(raw) == "nested"

    def test_parse_ai_content_json_summary_key(self):
        raw = '{"summary": "old format"}'
        assert Summary.parse_ai_content(raw) == "old format"

    def test_parse_ai_content_empty(self):
        assert Summary.parse_ai_content("") == ""
        assert Summary.parse_ai_content(None) == ""

    def test_parse_ai_content_invalid_json(self):
        assert Summary.parse_ai_content("{broken") == "{broken"


class TestTag:
    def test_from_api(self):
        t = Tag.model_validate({"id": "t1", "name": "Work", "file_count": 5})
        assert t.recording_count == 5


class TestAnalysisStatus:
    def test_complete(self):
        s = AnalysisStatus.model_validate({"status": 1, "msg": "task complete"})
        assert s.complete is True
        assert s.message == "task complete"

    def test_processing(self):
        s = AnalysisStatus.model_validate({"status": 0, "msg": "task processing"})
        assert s.complete is False
