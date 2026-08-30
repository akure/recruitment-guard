from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ops.events import make_event
from ops.ingest import ingest_packet


def _packet_path(value: str, base: Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else (base / path).resolve()


def _record(path: Path, source: str) -> dict[str, Any]:
    normalized = ingest_packet(path)
    normalized["ingestion_source"] = source
    normalized["packet_path"] = str(path.resolve())
    normalized["events"] = [
        make_event(
            normalized["packet_id"],
            "packet_ingested",
            "system",
            {"source": source, "source_files": normalized["source_files"]},
        )
    ]
    return normalized


def _paths_from_manifest(path: Path) -> list[Path]:
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        values = [row.get("packet_path") or row.get("packet_dir") or row.get("path") for row in rows]
    elif path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("packets", payload) if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise ValueError("JSON manifest must be a list or an object with a packets list")
        values = [
            row.get("packet_path") or row.get("packet_dir") or row.get("path")
            if isinstance(row, dict)
            else row
            for row in rows
        ]
    else:
        raise ValueError(f"unsupported import manifest: {path.suffix}")
    if not values or any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError("each import row must provide packet_path, packet_dir, or path")
    return [_packet_path(value, path.parent) for value in values]


def discover_packet_paths(source: Path) -> tuple[list[Path], str]:
    source = source.expanduser().resolve()
    if source.is_dir():
        if (source / "profile.json").exists() and (source / "consent.json").exists():
            return [source], "folder"
        paths = sorted(path for path in source.glob("packet_*") if path.is_dir())
        if not paths:
            raise ValueError(f"no packet_* directories found in {source}")
        return paths, "folder"
    if source.is_file() and source.suffix.lower() in {".csv", ".json"}:
        return _paths_from_manifest(source), source.suffix.lower().lstrip(".")
    raise ValueError(f"source must be a packet folder, a folder of packets, CSV, or JSON: {source}")


def import_source(source: Path) -> list[dict[str, Any]]:
    paths, source_type = discover_packet_paths(source)
    return [_record(path, source_type) for path in paths]


__all__ = ["discover_packet_paths", "import_source"]
