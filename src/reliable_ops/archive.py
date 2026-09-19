from __future__ import annotations

import hashlib
from pathlib import Path


def archive_bytes(root: str | Path, source_id: str, payload: bytes) -> Path:
    """Write immutable, content-addressed evidence for a synthetic source artifact."""
    digest = hashlib.sha256(payload).hexdigest()
    directory = Path(root) / source_id
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / f"{digest}.bin"
    if not destination.exists():
        destination.write_bytes(payload)
    return destination
