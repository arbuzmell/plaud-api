"""API endpoint constants for Plaud.

The default base URL is ``https://api.plaud.ai``.  Users in certain regions
(e.g. Southeast Asia) are served by regional mirrors such as
``https://api-apse1.plaud.ai``.  Call :func:`set_base_url` to switch all
endpoint constants at once — this must be done **before** creating a
:class:`~plaud.client.PlaudClient`.
"""

from __future__ import annotations

import sys

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

# Known regional base URLs returned by the API in
# ``-302 user region mismatch`` responses.
KNOWN_REGIONS = {
    "default": "https://api.plaud.ai",
    "apse1": "https://api-apse1.plaud.ai",  # Asia-Pacific Southeast 1
}


def set_base_url(base_url: str) -> None:
    """Rewrite every endpoint constant to use *base_url*.

    This updates the module-level constants **and** patches any submodule
    that already imported them via ``from plaud._endpoints import ...``
    (Python ``from``-imports copy the value at import time).

    Args:
        base_url: New API base URL, e.g. ``"https://api-apse1.plaud.ai"``.
            Must **not** end with a trailing slash.
    """
    base_url = base_url.rstrip("/")
    old_base = globals()["API_BASE"]
    if base_url == old_base:
        return

    # 1. Patch this module's constants.
    for name, value in list(globals().items()):
        if isinstance(value, str) and old_base in value:
            globals()[name] = value.replace(old_base, base_url)

    # 2. Patch already-imported submodules that copied these constants.
    for mod_name, mod in list(sys.modules.items()):
        if mod is None or not mod_name.startswith("plaud."):
            continue
        if mod_name == __name__:
            continue
        for attr in list(vars(mod)):
            val = getattr(mod, attr, None)
            if isinstance(val, str) and old_base in val:
                setattr(mod, attr, val.replace(old_base, base_url))
