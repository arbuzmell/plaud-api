"""Speakers API — list speakers, rename in recordings."""

from __future__ import annotations

from builtins import list as list_type
from typing import TYPE_CHECKING, Any, cast

from plaud._endpoints import FILE_DETAIL, FILE_LIST, SPEAKER_LIST
from plaud.exceptions import NotFoundError
from plaud.models import Speaker

if TYPE_CHECKING:
    from plaud.session import PlaudSession


class SpeakersAPI:
    """Operations on Plaud speakers.

    Speaker names live in each recording's transcription segments.
    Use ``rename()`` to change a speaker's name in a specific recording.
    Use ``list()`` to see the global speaker list (read-only, used for
    voice identification).
    """

    def __init__(self, session: PlaudSession) -> None:
        self._s = session

    def list(self) -> list_type[Speaker]:
        """Get all known speakers from Plaud cloud."""
        data = self._s.get(SPEAKER_LIST)
        return [
            Speaker(id=s.get("id", ""), name=s.get("name", ""))
            for s in data.get("data_speaker_list", [])
        ]

    def get_for_recording(self, file_id: str) -> list_type[dict[str, Any]]:
        """Extract unique speakers from a recording's transcription.

        Returns:
            List of dicts ``[{"name": "...", "segments_count": N}, ...]``
            sorted by segment count (descending).
        """
        data = self._s.post(FILE_LIST, json=[file_id], timeout=60)
        files = data["data_file_list"]
        if not files:
            raise NotFoundError(f"Recording not found: {file_id}")

        trans_result = files[0].get("trans_result") or []
        stats: dict[str, int] = {}
        for seg in trans_result:
            speaker = (seg.get("speaker") or "").strip()
            if speaker:
                stats[speaker] = stats.get(speaker, 0) + 1

        return [
            {"name": name, "segments_count": count}
            for name, count in sorted(stats.items(), key=lambda x: -x[1])
        ]

    def rename(
        self,
        file_id: str,
        old_name: str,
        new_name: str,
    ) -> dict[str, Any]:
        """Rename a speaker in a recording's transcription.

        Fetches the recording's ``trans_result``, replaces all occurrences
        of ``old_name`` with ``new_name`` in segment speaker fields,
        and saves the updated transcription back.

        Args:
            file_id: The recording ID.
            old_name: Current speaker name in the transcription.
            new_name: New speaker name.

        Returns:
            Updated file data from the API.

        Raises:
            NotFoundError: if the recording is not found.
            ValueError: if old_name is not found in the transcription.
        """
        data = self._s.post(FILE_LIST, json=[file_id], timeout=60)
        files = data["data_file_list"]
        if not files:
            raise NotFoundError(f"Recording not found: {file_id}")

        trans_result = files[0].get("trans_result") or []
        renamed = 0
        for seg in trans_result:
            if (seg.get("speaker") or "").strip() == old_name:
                seg["speaker"] = new_name
                renamed += 1

        if renamed == 0:
            raise ValueError(
                f"Speaker '{old_name}' not found in recording {file_id}"
            )

        result = self._s.patch(
            f"{FILE_DETAIL}/{file_id}",
            json={"trans_result": trans_result},
        )
        return cast(dict[str, Any], result.get("data_file", result))
