"""Tags API — list tags, get recordings by tag."""

from __future__ import annotations

from builtins import list as list_type
from typing import TYPE_CHECKING

from plaud._endpoints import FILE_SIMPLE, FILETAG
from plaud.models import Tag

if TYPE_CHECKING:
    from plaud.session import PlaudSession


class TagsAPI:
    """Operations on Plaud tags (folders)."""

    def __init__(self, session: PlaudSession) -> None:
        self._s = session

    def list(self) -> list_type[Tag]:
        """Get all tags."""
        data = self._s.get(FILETAG)
        return [Tag.model_validate(t) for t in data["data_filetag_list"]]

    def get_recordings(self, tag_id: str) -> list_type[str]:
        """Get recording IDs that belong to a tag.

        Args:
            tag_id: The tag ID.

        Returns:
            List of recording (file) IDs.
        """
        data = self._s.get(
            FILE_SIMPLE,
            params={
                "skip": 0,
                "limit": 99999,
                "is_trash": 0,
                "sort_by": "start_time",
                "is_desc": "true",
            },
        )
        return [
            f["id"]
            for f in data["data_file_list"]
            if tag_id in f.get("filetag_id_list", [])
        ]
