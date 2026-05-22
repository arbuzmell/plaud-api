"""Shared fixtures for Plaud API tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from plaud.session import PlaudSession


@pytest.fixture()
def mock_session() -> MagicMock:
    """A mocked PlaudSession that doesn't make real HTTP requests."""
    return MagicMock(spec=PlaudSession)


# ---------------------------------------------------------------------------
# Sample API response data
# ---------------------------------------------------------------------------

SAMPLE_FILE_SIMPLE = {
    "id": "abc123",
    "filename": "Team Standup",
    "filesize": 4200000,
    "duration": 185000,  # 3:05
    "start_time": 1738900000000,
    "is_trans": 1,
    "is_summary": 1,
    "filetag_id_list": ["tag_work"],
}

SAMPLE_FILE_DETAIL = {
    **SAMPLE_FILE_SIMPLE,
    "trans_result": [
        {
            "speaker": "Alice",
            "content": "Good morning everyone.",
            "start_time": 0,
            "end_time": 3000,
        },
        {
            "speaker": "Bob",
            "content": "Morning! Let's start with updates.",
            "start_time": 3100,
            "end_time": 6000,
        },
    ],
    "ai_content": '{"markdown": "## Meeting Summary\\n\\nDiscussed project updates."}',
    "summary_list": [],
}

SAMPLE_SPEAKER = {"id": "spk_001", "name": "Alice", "embedding": [0.1, 0.2]}

SAMPLE_TAG = {"id": "tag_work", "name": "Work Meetings", "file_count": 12}

SAMPLE_ANALYSIS_COMPLETE = {
    "status": 1,
    "msg": "task complete",
    "data_result": [
        {"speaker": "Alice", "content": "Hello"},
    ],
    "data_result_summ": '{"markdown": "Summary text"}',
    "outline_result": [],
    "task_id_info": {},
}

SAMPLE_ANALYSIS_SUCCESS_STATUS_NEGATIVE = {
    "status": -111,
    "msg": "success",
    "data_result": [
        {"speaker": "Speaker 1", "content": "This is a short Plaud API test."},
    ],
    "data_result_summ": "",
    "outline_result": [],
    "task_id_info": {},
}

SAMPLE_ANALYSIS_PROCESSING = {
    "status": 0,
    "msg": "task processing",
}


@pytest.fixture()
def sample_file_simple() -> dict[str, Any]:
    return dict(SAMPLE_FILE_SIMPLE)


@pytest.fixture()
def sample_file_detail() -> dict[str, Any]:
    return dict(SAMPLE_FILE_DETAIL)
