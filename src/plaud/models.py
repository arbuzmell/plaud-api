"""Pydantic models for Plaud API responses."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, model_validator


class Recording(BaseModel):
    """A Plaud recording (file)."""

    id: str
    filename: str = ""
    duration_ms: int = Field(0, alias="duration")
    filesize: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    has_transcription: bool = False
    has_summary: bool = False
    tag_ids: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}

    @model_validator(mode="before")
    @classmethod
    def _from_api(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, dict):
            # Map start_time (epoch ms) → created_at
            if "start_time" in data and "created_at" not in data:
                ts = data["start_time"]
                if isinstance(ts, (int, float)) and ts > 0:
                    data["created_at"] = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            # Map is_trans / is_summary → booleans
            if "is_trans" in data:
                data["has_transcription"] = bool(data["is_trans"])
            if "is_summary" in data:
                data["has_summary"] = bool(data["is_summary"])
            if "filetag_id_list" in data:
                data["tag_ids"] = data["filetag_id_list"]
        return data

    @property
    def duration_seconds(self) -> float:
        return self.duration_ms / 1000

    @property
    def duration_display(self) -> str:
        total_sec = self.duration_ms // 1000
        minutes, seconds = divmod(total_sec, 60)
        return f"{minutes}:{seconds:02d}"


class TranscriptionSegment(BaseModel):
    """A single segment of a transcription."""

    speaker: str = ""
    text: str = Field("", alias="content")
    start_time_ms: int = Field(0, alias="start_time")
    end_time_ms: int = Field(0, alias="end_time")

    model_config = {"populate_by_name": True}


class Transcription(BaseModel):
    """Full transcription for a recording."""

    recording_id: str = ""
    segments: list[TranscriptionSegment] = Field(default_factory=list)
    language: str = ""


class Summary(BaseModel):
    """AI-generated summary for a recording."""

    recording_id: str = ""
    content: str = ""

    @staticmethod
    def parse_ai_content(raw: str | Any) -> str:
        """Extract markdown text from Plaud's ai_content field.

        The field can be plain markdown or a JSON string with varying schemas.
        """
        if not raw:
            return ""
        if not isinstance(raw, str):
            return str(raw)
        if not raw.strip().startswith("{"):
            return raw
        try:
            parsed = json.loads(raw)
            if "markdown" in parsed:
                return parsed["markdown"]
            if "content" in parsed and isinstance(parsed["content"], dict):
                return parsed["content"].get("markdown", raw)
            if "summary" in parsed:
                return parsed["summary"]
            return raw
        except (json.JSONDecodeError, TypeError):
            return raw


class Speaker(BaseModel):
    """A speaker from the Plaud speaker list."""

    id: str = ""
    name: str = ""


class Tag(BaseModel):
    """A tag (folder) in Plaud."""

    id: str = ""
    name: str = ""
    recording_count: int = 0

    @model_validator(mode="before")
    @classmethod
    def _from_api(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, dict):
            if "file_count" in data and "recording_count" not in data:
                data["recording_count"] = data["file_count"]
        return data


class AnalysisStatus(BaseModel):
    """Status of a transcription/summary analysis job."""

    complete: bool = False
    message: str = ""
    raw: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _from_api(cls, data: dict[str, Any]) -> dict[str, Any]:
        if isinstance(data, dict):
            is_complete = data.get("status") == 1 or (
                data.get("msg") == "success" and "data_result" in data
            )
            return {
                "complete": is_complete,
                "message": data.get("msg", ""),
                "raw": data,
            }
        return data
