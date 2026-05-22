"""Transcriptions API — start analysis, poll status, get results."""

from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING, Any, cast

from plaud._endpoints import AI_TRANSSUMM, FILE_DETAIL, FILE_LIST
from plaud.exceptions import AnalysisTimeoutError, NotFoundError
from plaud.models import (
    AnalysisStatus,
    Summary,
    Transcription,
    TranscriptionSegment,
)

if TYPE_CHECKING:
    from plaud.session import PlaudSession


class TranscriptionsAPI:
    """Operations on transcriptions and AI summaries."""

    def __init__(self, session: PlaudSession) -> None:
        self._s = session

    def start(self, file_id: str, *, language: str = "en") -> dict[str, Any]:
        """Start transcription and analysis for a recording.

        Args:
            file_id: The recording ID.
            language: Language code (e.g. "en", "ru", "zh", "ja").

        Returns:
            Raw API response data.
        """
        data = self._s.patch(
            f"{FILE_DETAIL}/{file_id}",
            json={
                "extra_data": {
                    "tranConfig": {
                        "language": language,
                        "type_type": "system",
                        "type": "REASONING-NOTE",
                        "diarization": 1,
                        "llm": "auto",
                    }
                }
            },
        )
        return cast(dict[str, Any], data.get("data_file", data))

    def get_status(self, file_id: str, *, language: str = "en") -> AnalysisStatus:
        """Check the current analysis status for a recording."""
        data = self._s.post(
            f"{AI_TRANSSUMM}/{file_id}",
            json={
                "is_reload": 0,
                "summ_type": "REASONING-NOTE",
                "summ_type_type": "system",
                "info": json.dumps({
                    "language": language,
                    "diarization": 1,
                    "llm": "auto",
                }),
                "support_mul_summ": True,
            },
        )
        return AnalysisStatus.model_validate(data)

    def wait(
        self,
        file_id: str,
        *,
        language: str = "en",
        timeout: int = 500,
        poll_interval: int = 10,
    ) -> dict[str, Any]:
        """Block until analysis completes, then return raw results.

        Args:
            file_id: The recording ID.
            language: Language code.
            timeout: Maximum wait time in seconds.
            poll_interval: Seconds between status checks.

        Returns:
            The raw analysis result dict containing ``data_result``,
            ``data_result_summ``, etc.

        Raises:
            AnalysisTimeoutError: if analysis doesn't complete in time.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            status = self.get_status(file_id, language=language)
            if status.complete:
                return status.raw
            time.sleep(poll_interval)

        raise AnalysisTimeoutError(
            f"Analysis for {file_id} did not complete within {timeout}s"
        )

    def save_results(self, file_id: str, analysis_result: dict[str, Any]) -> dict[str, Any]:
        """Save analysis results back to the recording.

        This is required after ``wait()`` to persist the transcription and
        summary to the Plaud cloud.
        """
        trans_result = analysis_result.get("data_result", [])
        raw_ai = analysis_result.get("data_result_summ", "")
        outline_result = analysis_result.get("outline_result", [])

        ai_content = raw_ai
        ai_content_header: dict[str, Any] = {}
        if isinstance(raw_ai, str) and raw_ai.strip().startswith("{"):
            try:
                parsed = json.loads(raw_ai)
                if "markdown" in parsed:
                    ai_content = parsed["markdown"]
                elif "content" in parsed and isinstance(parsed["content"], dict):
                    ai_content = parsed["content"].get("markdown", raw_ai)
                else:
                    ai_content = parsed.get("summary", raw_ai)
                ai_content_header = parsed.get("header", {})
            except (json.JSONDecodeError, TypeError):
                pass

        data = self._s.patch(
            f"{FILE_DETAIL}/{file_id}",
            json={
                "trans_result": trans_result,
                "ai_content": ai_content,
                "outline_result": outline_result,
                "support_mul_summ": True,
                "extra_data": {
                    "task_id_info": analysis_result.get("task_id_info", {}),
                    "aiContentHeader": ai_content_header,
                },
            },
        )
        return cast(dict[str, Any], data.get("data_file", data))

    # ------------------------------------------------------------------
    # High-level getters
    # ------------------------------------------------------------------

    def get(self, file_id: str) -> Transcription:
        """Get the full transcription for a recording.

        Fetches the recording details and parses ``trans_result`` into
        a structured ``Transcription`` model.
        """
        raw = self._get_raw_file(file_id)
        segments = [
            TranscriptionSegment.model_validate(seg)
            for seg in (raw.get("trans_result") or [])
        ]
        return Transcription(recording_id=file_id, segments=segments)

    def get_summary(self, file_id: str) -> Summary:
        """Get the AI summary for a recording."""
        raw = self._get_raw_file(file_id)
        raw_content = raw.get("ai_content") or ""
        if not raw_content:
            summary_list = raw.get("summary_list") or []
            raw_content = summary_list[0] if summary_list else ""
        content = Summary.parse_ai_content(raw_content)
        return Summary(recording_id=file_id, content=content)

    def update_transcript(
        self, file_id: str, segments: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Update the transcription segments for a recording.

        Useful for correcting speaker names in transcripts.
        """
        data = self._s.patch(
            f"{FILE_DETAIL}/{file_id}",
            json={"trans_result": segments},
        )
        return cast(dict[str, Any], data.get("data_file", data))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_raw_file(self, file_id: str) -> dict[str, Any]:
        data = self._s.post(FILE_LIST, json=[file_id], timeout=60)
        files = data["data_file_list"]
        if not files:
            raise NotFoundError(f"Recording not found: {file_id}")
        return cast(dict[str, Any], files[0])
