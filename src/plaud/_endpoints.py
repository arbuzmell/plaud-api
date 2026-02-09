"""API endpoint constants for Plaud."""

API_BASE = "https://api.plaud.ai"

# Files / Recordings
FILE_SIMPLE = f"{API_BASE}/file/simple/web"
FILE_LIST = f"{API_BASE}/file/list"
FILE_DETAIL = f"{API_BASE}/file"  # /{file_id}  (GET detail, PATCH update)
FILE_UPLOAD_URL = f"{API_BASE}/file/get_upload_presigned_url"
FILE_MERGE = f"{API_BASE}/file/merge_multipart"
FILE_CONFIRM = f"{API_BASE}/file/confirm_upload"
FILE_TEMP_URL = f"{API_BASE}/file/temp-url"  # /{file_id}

# AI / Analysis
AI_TRANSSUMM = f"{API_BASE}/ai/transsumm"  # /{file_id}

# Tags
FILETAG = f"{API_BASE}/filetag/"

# Speakers
SPEAKER_LIST = f"{API_BASE}/speaker/list"
SPEAKER_SYNC = f"{API_BASE}/speaker/sync"

