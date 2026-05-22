"""API endpoint constants for Plaud."""

from __future__ import annotations

API_BASE = "https://api.plaud.ai"

KNOWN_REGIONS = {
    "default": API_BASE,
    "apse1": "https://api-apse1.plaud.ai",
}

# Files / Recordings
FILE_SIMPLE = "/file/simple/web"
FILE_LIST = "/file/list"
FILE_DETAIL = "/file"  # /{file_id}  (GET detail, PATCH update)
FILE_UPLOAD_URL = "/file/get_upload_presigned_url"
FILE_MERGE = "/file/merge_multipart"
FILE_CONFIRM = "/file/confirm_upload"
FILE_TEMP_URL = "/file/temp-url"  # /{file_id}

# AI / Analysis
AI_TRANSSUMM = "/ai/transsumm"  # /{file_id}

# Tags
FILETAG = "/filetag/"

# Speakers
SPEAKER_LIST = "/speaker/list"
SPEAKER_SYNC = "/speaker/sync"
