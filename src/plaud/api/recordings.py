"""Recordings API — list, get, upload, download audio."""

from __future__ import annotations

import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from plaud._endpoints import (
    FILE_CONFIRM,
    FILE_LIST,
    FILE_MERGE,
    FILE_SIMPLE,
    FILE_TEMP_URL,
    FILE_UPLOAD_URL,
)
from plaud.exceptions import NotFoundError, UploadError
from plaud.models import Recording

if TYPE_CHECKING:
    from plaud.session import PlaudSession


class RecordingsAPI:
    """Operations on Plaud recordings (files)."""

    def __init__(self, session: PlaudSession) -> None:
        self._s = session

    # ------------------------------------------------------------------
    # List / Get
    # ------------------------------------------------------------------

    def list(
        self,
        *,
        limit: int = 50,
        skip: int = 0,
        sort_by: str = "start_time",
        descending: bool = True,
    ) -> list[Recording]:
        """List recordings (most recent first by default)."""
        data = self._s.get(
            FILE_SIMPLE,
            params={
                "skip": skip,
                "limit": limit,
                "is_trash": 0,
                "sort_by": sort_by,
                "is_desc": str(descending).lower(),
            },
        )
        return [Recording.model_validate(f) for f in data["data_file_list"]]

    def get(self, file_id: str) -> Recording:
        """Get a single recording by ID (with full details)."""
        details = self.get_details([file_id])
        if not details:
            raise NotFoundError(f"Recording not found: {file_id}")
        return details[0]

    def get_details(self, file_ids: list[str]) -> list[Recording]:
        """Get full details for a batch of recording IDs."""
        if not file_ids:
            return []
        data = self._s.post(FILE_LIST, json=file_ids, timeout=60)
        return [Recording.model_validate(f) for f in data["data_file_list"]]

    def get_raw(self, file_id: str) -> dict[str, Any]:
        """Get raw API response for a recording (includes trans_result, ai_content, etc.)."""
        data = self._s.post(FILE_LIST, json=[file_id], timeout=60)
        files = data["data_file_list"]
        if not files:
            raise NotFoundError(f"Recording not found: {file_id}")
        return files[0]

    # ------------------------------------------------------------------
    # Audio URL
    # ------------------------------------------------------------------

    def get_audio_url(self, file_id: str) -> str:
        """Get a temporary presigned S3 URL for downloading the audio file."""
        data = self._s.get(f"{FILE_TEMP_URL}/{file_id}")
        return data["temp_url"]

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    def upload(
        self,
        file_path: str | Path,
        *,
        name: str | None = None,
    ) -> Recording:
        """Upload an audio file to Plaud.

        Args:
            file_path: Path to an MP3 or OPUS file.
            name: Display name for the recording. Defaults to a date-based name.

        Returns:
            The newly created Recording.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = file_path.suffix.lower()
        file_type = "OPUS" if ext in {".asr", ".opus"} else "MP3"
        file_size = file_path.stat().st_size

        # Step 1: Get presigned URL
        upload_data = self._s.post(
            FILE_UPLOAD_URL,
            json={"filesize": file_size, "file_type": file_type},
        )["data"]
        upload_url = upload_data["part_urls"][0]
        upload_id = upload_data["upload_id"]
        object_name = upload_data["object_name"]

        # Step 2: Upload to S3
        with open(file_path, "rb") as f:
            resp = self._s.put_raw(
                upload_url,
                data=f,
                headers={"Content-Type": "application/octet-stream"},
            )
        if resp.status_code != 200:
            raise UploadError(f"S3 upload failed: {resp.status_code} {resp.text[:200]}")
        etag = resp.headers.get("ETag", "").strip('"')

        # Step 3: Merge multipart
        self._s.post(
            FILE_MERGE,
            json={
                "upload_id": upload_id,
                "object_name": object_name,
                "parts": [{"Etag": etag, "PartNumber": 1}],
            },
        )

        # Step 4: Confirm upload
        if name is None:
            name = f"Meeting {datetime.now().strftime('%d.%m.%Y')}"

        timestamp_ms = int(time.time() * 1000)
        result = self._s.post(
            FILE_CONFIRM,
            json={
                "upload_id": upload_id,
                "object_name": object_name,
                "scene": 101,
                "is_tmp": 0,
                "support_mul_summ": True,
                "file_type": file_type,
                "filename": name,
                "start_time": timestamp_ms,
                "session_id": int(timestamp_ms / 1000),
                "serial_number": str(uuid.uuid4()),
            },
        )
        return Recording.model_validate(result["data"])
