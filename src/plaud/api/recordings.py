"""Recordings API — list, get, upload, download audio."""

from __future__ import annotations

import time
import uuid
from builtins import list as list_type
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

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


# S3 multipart part size; the presign endpoint returns one URL per chunk of this size.
UPLOAD_PART_SIZE = 5 * 1024 * 1024


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
    ) -> list_type[Recording]:
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

    def get_details(self, file_ids: list_type[str]) -> list_type[Recording]:
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
        return cast(dict[str, Any], files[0])

    # ------------------------------------------------------------------
    # Audio URL
    # ------------------------------------------------------------------

    def get_audio_url(self, file_id: str) -> str:
        """Get a temporary presigned S3 URL for downloading the audio file."""
        data = self._s.get(f"{FILE_TEMP_URL}/{file_id}")
        return str(data["temp_url"])

    # ------------------------------------------------------------------
    # Upload
    # ------------------------------------------------------------------

    def upload(
        self,
        file_path: str | Path,
        *,
        name: str | None = None,
        start_time: datetime | None = None,
    ) -> Recording:
        """Upload an audio file to Plaud.

        Files larger than one part (5 MiB) are sent as a multipart upload, one
        part per presigned URL the API returns.

        Args:
            file_path: Path to an MP3 or OPUS file.
            name: Display name for the recording. Defaults to a date-based name.
            start_time: When the recording started. Plaud sorts and dates the
                recording by this. Defaults to now. Naive datetimes are treated
                as local time.

        Returns:
            The newly created Recording.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = file_path.suffix.lower()
        file_type = "OPUS" if ext in {".asr", ".opus"} else "MP3"
        file_size = file_path.stat().st_size

        # Step 1: Get presigned URLs, one per UPLOAD_PART_SIZE chunk
        upload_data = self._s.post(
            FILE_UPLOAD_URL,
            json={"filesize": file_size, "file_type": file_type},
        )["data"]
        part_urls = upload_data["part_urls"]
        upload_id = upload_data["upload_id"]
        object_name = upload_data["object_name"]

        expected_parts = max(1, -(-file_size // UPLOAD_PART_SIZE))
        if len(part_urls) != expected_parts:
            raise UploadError(
                f"Expected {expected_parts} upload part URLs for {file_size} bytes, "
                f"got {len(part_urls)}"
            )

        # Step 2: Upload each part to S3
        parts = []
        with open(file_path, "rb") as f:
            for number, url in enumerate(part_urls, start=1):
                resp = self._s.put_raw(
                    url,
                    data=f.read(UPLOAD_PART_SIZE),
                    headers={"Content-Type": "application/octet-stream"},
                )
                if resp.status_code != 200:
                    raise UploadError(
                        f"S3 upload of part {number}/{len(part_urls)} failed: "
                        f"{resp.status_code} {resp.text[:200]}"
                    )
                etag = resp.headers.get("ETag", "").strip('"')
                parts.append({"Etag": etag, "PartNumber": number})

        # Step 3: Merge multipart
        self._s.post(
            FILE_MERGE,
            json={
                "upload_id": upload_id,
                "object_name": object_name,
                "parts": parts,
            },
        )

        # Step 4: Confirm upload
        if name is None:
            name = f"Meeting {datetime.now().strftime('%d.%m.%Y')}"

        timestamp_ms = (
            int(start_time.timestamp() * 1000) if start_time else int(time.time() * 1000)
        )
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
