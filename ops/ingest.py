from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ops.consent import validate_consent


def ingest_packet(packet: Path) -> dict[str, Any]:
    if not packet.is_dir():
        raise ValueError(f"packet directory does not exist: {packet}")
    manifest = json.loads((packet.parent / "MANIFEST.json").read_text(encoding="utf-8"))
    profile = json.loads((packet / "profile.json").read_text(encoding="utf-8"))
    consent = json.loads((packet / "consent.json").read_text(encoding="utf-8"))
    validate_consent(consent)
    packet_id = packet.name.rsplit("_", 1)[-1]
    entry = next(item for item in manifest["packets"] if item["packet_id"] == packet_id)
    return {
        "schema_version": "ops.v1",
        "packet_id": packet_id,
        "profile_id": profile["profile_id"],
        "role_family": entry["role_family"],
        "ingestion_source": "folder",
        "source_files": sorted(path.name for path in packet.iterdir() if path.is_file() and path.name != "ground_truth.json"),
        "consent_status": consent["status"],
        "consent_id": consent["consent_id"],
        "synthetic_only": bool(entry["synthetic_only"]),
    }
