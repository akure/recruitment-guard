from __future__ import annotations

import argparse
import json
import time
from datetime import date
from pathlib import Path
from typing import Callable

from checkpoint.workflow import Assessment, ExtractedFact, create_pending_review, finalize_packet
from extraction.extract import extract_document
from validator.validate import ValidatorFinding, validate


def _assessment(data_root: Path, packet_id: str) -> Assessment | None:
    path = data_root / f"packet_{packet_id}" / "assessment.json"
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    return Assessment(raw["score"], date.fromisoformat(raw["date"]))


def _facts(artifact: dict, doc: str) -> list[ExtractedFact]:
    return [
        ExtractedFact(
            fact_id=fact["fact_id"], subject=fact["subject"], claim=fact["claim"],
            source_doc=doc, source_span=fact["source_span"],
        )
        for fact in artifact[doc]["facts"]
    ]


def _write_trajectory(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_packet(
    packet_id: str,
    *,
    data_root: Path = Path("data"),
    extraction_root: Path = Path("extraction/output"),
    pending_root: Path = Path("pending_review"),
    brief_root: Path = Path("briefs"),
    trajectory_root: Path = Path("trajectories"),
    mock: bool = False,
    as_of: date | None = None,
    conflict_fn: Callable[[str, str], bool] | None = None,
) -> dict:
    packet_id = packet_id.zfill(2)
    packet = data_root / f"packet_{packet_id}"
    if not packet.exists():
        raise FileNotFoundError(packet)
    started = time.perf_counter()
    trajectory_path = trajectory_root / f"packet_{packet_id}.json"
    trajectory = {
        "packet_id": packet_id,
        "state": "running",
        "stage_1_extraction": {"cv": None, "transcript": None},
        "stage_2_validation": [],
        "stage_3_pause": {"paused": False, "resolved_by": None, "resolution_notes": []},
        "stage_4_final_brief": None,
        "model_calls": [],
    }

    extraction_artifact = {"packet_id": packet_id, "cv": None, "transcript": None, "model_calls": []}
    for doc in ("cv", "transcript"):
        result, usage = extract_document(packet / f"{doc}.md", doc, packet_id, mock=mock)
        extraction_artifact[doc] = result
        call = {"stage": "extraction", "doc": doc, **usage}
        extraction_artifact["model_calls"].append(call)
        trajectory["model_calls"].append(call)
    extraction_path = extraction_root / f"packet_{packet_id}.json"
    extraction_path.parent.mkdir(parents=True, exist_ok=True)
    extraction_path.write_text(json.dumps(extraction_artifact, indent=2) + "\n", encoding="utf-8")
    trajectory["stage_1_extraction"] = {"cv": extraction_artifact["cv"], "transcript": extraction_artifact["transcript"]}
    _write_trajectory(trajectory_path, trajectory)

    assessment = _assessment(data_root, packet_id)
    findings = validate(
        _facts(extraction_artifact, "cv"), _facts(extraction_artifact, "transcript"), assessment,
        as_of=as_of, conflict_fn=conflict_fn,
    )
    trajectory["stage_2_validation"] = [finding.as_dict() for finding in findings]
    _write_trajectory(trajectory_path, trajectory)

    if findings:
        pending_path = create_pending_review(packet_id, findings, pending_root / f"packet_{packet_id}.json")
        trajectory["state"] = "pending_review"
        trajectory["stage_3_pause"] = {"paused": True, "pending_review": str(pending_path), "resolved_by": None, "resolution_notes": []}
        trajectory["elapsed_seconds"] = round(time.perf_counter() - started, 6)
        _write_trajectory(trajectory_path, trajectory)
        return {"state": "pending_review", "pending_path": str(pending_path), "trajectory_path": str(trajectory_path)}

    brief_path = finalize_packet(
        packet_id, None, brief_root / f"brief_guarded_{packet_id}.md",
        _facts(extraction_artifact, "cv"), _facts(extraction_artifact, "transcript"), assessment,
    )
    trajectory["state"] = "finalized"
    trajectory["stage_4_final_brief"] = str(brief_path)
    trajectory["elapsed_seconds"] = round(time.perf_counter() - started, 6)
    _write_trajectory(trajectory_path, trajectory)
    return {"state": "finalized", "brief_path": str(brief_path), "trajectory_path": str(trajectory_path)}


def resume_packet(
    packet_id: str,
    pending_path: Path,
    extraction_root: Path,
    data_root: Path,
    brief_root: Path,
    trajectory_root: Path,
) -> dict:
    packet_id = packet_id.zfill(2)
    extraction_artifact = json.loads((extraction_root / f"packet_{packet_id}.json").read_text(encoding="utf-8"))
    assessment = _assessment(data_root, packet_id)
    brief_path = finalize_packet(
        packet_id, pending_path, brief_root / f"brief_guarded_{packet_id}.md",
        _facts(extraction_artifact, "cv"), _facts(extraction_artifact, "transcript"), assessment,
    )
    trajectory_path = trajectory_root / f"packet_{packet_id}.json"
    trajectory = json.loads(trajectory_path.read_text(encoding="utf-8"))
    payload = json.loads(pending_path.read_text(encoding="utf-8"))
    notes = [finding["resolution"] for finding in payload.get("findings", []) if finding.get("resolution")]
    trajectory["state"] = "finalized"
    trajectory["stage_3_pause"] = {
        "paused": True, "pending_review": str(pending_path), "resolved_by": "recruiter", "resolution_notes": notes,
    }
    trajectory["stage_4_final_brief"] = str(brief_path)
    _write_trajectory(trajectory_path, trajectory)
    return {"state": "finalized", "brief_path": str(brief_path), "trajectory_path": str(trajectory_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one packet through the guarded pipeline.")
    parser.add_argument("packet_id")
    parser.add_argument("--mock", action="store_true", help="use deterministic local extraction")
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--extraction-root", default="extraction/output")
    parser.add_argument("--pending-root", default="pending_review")
    parser.add_argument("--brief-root", default="briefs")
    parser.add_argument("--trajectory-root", default="trajectories")
    args = parser.parse_args()
    result = run_packet(
        args.packet_id, data_root=Path(args.data_root), extraction_root=Path(args.extraction_root),
        pending_root=Path(args.pending_root), brief_root=Path(args.brief_root),
        trajectory_root=Path(args.trajectory_root), mock=args.mock,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
