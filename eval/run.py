from __future__ import annotations

import argparse
import json
import re
import tempfile
import time
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from baseline.run import llm_brief, mock_brief
from eval.harness import render_metrics, evaluate_records
from guarded.runner import run_packet


PLANTED_PACKETS = {"01", "02", "03"}


def _baseline_surface(text: str) -> bool:
    # Do not score the baseline's mandatory disclaimer; score only its candidate summary.
    summary = text.split("### Note", 1)[0]
    return bool(re.search(r"\b(contradiction|conflict|inconsistent|stale|missing assessment|flagged for review)\b", summary, re.I))


def run_evaluation(data_root: Path, output_root: Path, mock: bool = True) -> tuple[list[dict], dict]:
    records: list[dict] = []
    output_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="recruitment-guard-eval-") as tmp:
        temp_root = Path(tmp)
        for packet_path in sorted(data_root.glob("packet_*")):
            packet_id = packet_path.name.rsplit("_", 1)[-1]
            cv = (packet_path / "cv.md").read_text(encoding="utf-8")
            transcript = (packet_path / "transcript.md").read_text(encoding="utf-8")

            start = time.perf_counter()
            baseline_error = None
            try:
                baseline_text = mock_brief(packet_id, cv, transcript) if mock else llm_brief(packet_id, cv, transcript)
            except Exception as exc:
                baseline_text = ""
                baseline_error = f"{type(exc).__name__}: {exc}"
            baseline_seconds = time.perf_counter() - start

            start = time.perf_counter()
            guarded_error = None
            try:
                guarded_result = run_packet(
                packet_id,
                data_root=data_root,
                extraction_root=temp_root / "extraction",
                pending_root=temp_root / "pending",
                brief_root=temp_root / "briefs",
                trajectory_root=temp_root / "trajectories",
                mock=mock,
                as_of=date(2026, 8, 30),
                )
            except Exception as exc:
                guarded_result = {"state": "error"}
                guarded_error = f"{type(exc).__name__}: {exc}"
            guarded_seconds = time.perf_counter() - start
            trajectory_path = temp_root / "trajectories" / f"packet_{packet_id}.json"
            trajectory = json.loads(trajectory_path.read_text(encoding="utf-8")) if trajectory_path.exists() else {}
            findings = trajectory.get("stage_2_validation", [])
            records.append({
                "packet_id": packet_id,
                "baseline_surface": _baseline_surface(baseline_text),
                "guarded_findings": findings,
                "baseline_time_seconds": baseline_seconds,
                "guarded_time_seconds": guarded_seconds,
                "baseline_tokens": 0,
                "guarded_tokens": sum(call.get("tokens_in", 0) + call.get("tokens_out", 0) for call in trajectory.get("model_calls", [])),
                "baseline_state": "finalized" if baseline_error is None else "error",
                "guarded_state": guarded_result["state"],
                "baseline_error": baseline_error,
                "guarded_error": guarded_error,
                "complete": baseline_error is None and guarded_error is None,
            })
    summary = evaluate_records(records)
    summary["complete_packets"] = sum(record["complete"] for record in records)
    summary["failed_packets"] = len(records) - summary["complete_packets"]
    (output_root / "results.json").write_text(json.dumps({"records": records, "summary": summary}, indent=2) + "\n", encoding="utf-8")
    (output_root / "metrics.md").write_text(render_metrics(summary), encoding="utf-8")
    return records, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run fair baseline-vs-guarded evaluation on packets 01-12.")
    parser.add_argument("--data-root", default="data")
    parser.add_argument("--output-root", default="eval")
    parser.add_argument("--live", action="store_true", help="use API-backed paths instead of deterministic mock mode")
    args = parser.parse_args()
    records, summary = run_evaluation(Path(args.data_root), Path(args.output_root), mock=not args.live)
    print(render_metrics(summary))
    print(f"records={len(records)} output={args.output_root}")


if __name__ == "__main__":
    main()
