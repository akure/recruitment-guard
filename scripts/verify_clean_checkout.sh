#!/usr/bin/env bash
set -euo pipefail

repo_url="${RECRUITMENT_GUARD_REPO_URL:-https://github.com/akure/recruitment-guard.git}"
ref="${RECRUITMENT_GUARD_REF:-main}"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

git clone --quiet --depth 1 --branch "$ref" "$repo_url" "$tmp_dir/recruitment-guard"
cd "$tmp_dir/recruitment-guard"
python3 -m unittest discover -s tests -q
python3 -m workflow.run data_ops/packet_001 --output-root "$tmp_dir/output" --as-of 2026-08-30 --owner recruiter >/dev/null
test -s "$tmp_dir/output/packet_001/brief.md"
python3 -m workflow.run data_ops/packet_004 --output-root "$tmp_dir/output-blocked" --as-of 2026-08-30 --owner recruiter >/dev/null
python3 -m workflow.run --output-root "$tmp_dir/output-blocked" --resolve-packet 004 --actor recruiter --resolution-note "Reviewer confirmed the evidence context." >/dev/null
test -s "$tmp_dir/output-blocked/packet_004/brief.md"
printf 'clean-checkout verification passed: commit %s\n' "$(git rev-parse --short HEAD)"
