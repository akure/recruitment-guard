from __future__ import annotations

import json
import shutil
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data_ops"
PROFILES = ["startup", "enterprise", "small_team"]
ROLE_FAMILIES = ["backend_platform", "product_engineering", "data_ml_infrastructure", "security_reliability"]
CONDITIONS = ["clean", "contradiction", "missing_consent", "stale_assessment", "unsupported_claim", "work_mode_mismatch", "sponsorship_routing", "hard_negative"]
NAMES = ["Mira Sol", "Jonah Reed", "Nia Park", "Oren Vale", "Ari Chen", "Tessa North", "Ravi Stone", "Lena Moss"]
COMPANIES = ["Juniper Arc", "Cinder Works", "Northstar Loop", "Harbor Metric", "Cloud Orchard", "Blue Lantern", "Quiet River", "Pine Relay"]

PROFILE_TEXT = {
    "startup": {
        "context": "A 70-person product company with a small engineering team and high ownership across ambiguous work.",
        "mode": "Remote-first with quarterly planning meetups; overlap with US Eastern time from 13:00–17:00 UTC.",
        "evidence": "end-to-end ownership, practical trade-offs, adaptability, and clear communication under ambiguity",
    },
    "enterprise": {
        "context": "A regulated company with multiple engineering groups, established interfaces, and change-management controls.",
        "mode": "Hybrid with two office days per week in the candidate's assigned hub and documented on-call rotation.",
        "evidence": "sustained depth, operational reliability, cross-functional delivery, and work within controlled change processes",
    },
    "small_team": {
        "context": "A six-person engineering group where each engineer contributes directly to product delivery and support.",
        "mode": "Remote-compatible with four hours of daily overlap and occasional customer or team sessions.",
        "evidence": "hands-on contribution, independent execution, concise communication, and pragmatic prioritization",
    },
}

ROLE_TEXT = {
    "backend_platform": ("Backend / Platform Engineer", "Go, Python, APIs, service reliability, and distributed systems"),
    "product_engineering": ("Product Engineer", "TypeScript, Python, product delivery, APIs, and user-facing iteration"),
    "data_ml_infrastructure": ("Data / ML Infrastructure Engineer", "Python, SQL, orchestration, data quality, and model-serving operations"),
    "security_reliability": ("Security / Reliability Engineer", "Linux, cloud controls, incident response, and reliable operations"),
}


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def packet_docs(packet_id: str, profile_id: str, role_id: str, condition: str) -> tuple[str, str, str]:
    name = NAMES[(int(packet_id) - 1) % len(NAMES)]
    company = COMPANIES[(int(packet_id) - 1) % len(COMPANIES)]
    role, stack = ROLE_TEXT[role_id]
    profile = PROFILE_TEXT[profile_id]
    work_mode = profile["mode"]
    if condition == "work_mode_mismatch":
        cv_mode = "Available for fully remote work from UTC+5; not available for recurring office attendance."
        transcript_mode = "I can travel occasionally, but I cannot commit to weekly office attendance."
    else:
        cv_mode = work_mode
        transcript_mode = "The stated work arrangement works for me, and I can plan around the expected overlap."
    if condition == "contradiction":
        cv_claim = "Owned the full migration plan and led the rollout across three services."
        transcript_claim = "I contributed implementation, while the staff engineer owned the migration plan and final rollout decisions."
    elif condition == "unsupported_claim":
        cv_claim = "Recognized expert in fault-tolerant multi-region systems at massive scale."
        transcript_claim = "I saw the dashboards and followed the existing runbook; I would want to confirm the exact design details."
    elif condition == "hard_negative":
        cv_claim = "Supported a service migration with a clear handoff to the owning team."
        transcript_claim = "I supported the migration and documented the handoff; another engineer owned the final rollout."
    else:
        cv_claim = "Designed and shipped a service change, documented the trade-offs, and measured the operational result."
        transcript_claim = "I designed the change with the team, explained the trade-offs, and stayed involved through the rollout."
    if condition == "sponsorship_routing":
        auth_cv = "Work authorization: candidate requests employer sponsorship for the role; do not infer nationality or immigration status."
        auth_tx = "I would need the recruiting team to confirm whether sponsorship is available for this role and jurisdiction."
    else:
        auth_cv = "Work authorization: candidate-provided status is recorded for recruiting operations only."
        auth_tx = "I can provide the requested work-authorization details through the recruiting process."
    jd = f"""# {role} — {profile_id.replace('_', ' ').title()} profile

## Context
{profile['context']}

## Must-have requirements
- {stack}
- Demonstrated delivery of production work with traceable ownership boundaries.
- Clear written and spoken communication about trade-offs, incidents, and uncertainty.
- {work_mode}

## Preferred requirements
- Experience in a domain with meaningful reliability, privacy, or operational constraints.
- Evidence of improving a team process without overstating personal ownership.
- {profile['evidence']}.

## Recruiting operations
- Work-authorization and sponsorship questions are handled as candidate-provided workflow facts with consent and jurisdictional review.
- This profile defines evidence questions; it does not define a candidate score or automated decision.
"""
    cv = f"""# {name}

## Summary
{role} with experience across production delivery, operational support, and cross-functional planning.

## Experience
### {company} — {role}
**2021–present**
- {cv_claim}
- Built runbooks, reviewed changes, and participated in incident retrospectives.
- Worked with product and operations partners to turn incomplete requirements into an executable plan.

## Work arrangement
- {cv_mode}
- {auth_cv}

## Selected technology
{stack}.
"""
    transcript = f"""# Interview transcript — {name}

**Interviewer:** Walk me through a project where your personal scope mattered.
**{name}:** {transcript_claim}

**Interviewer:** How did you communicate uncertainty or operational risk?
**{name}:** I documented the unknowns, asked for review where the impact was material, and updated the plan when evidence changed.

**Interviewer:** What working arrangement can you support?
**{name}:** {transcript_mode}

**Interviewer:** What should recruiting confirm before advancing the process?
**{name}:** {auth_tx}
"""
    return jd, cv, transcript


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "profiles").mkdir(parents=True)
    (OUT / "role_families").mkdir(parents=True)
    for profile_id, profile in PROFILE_TEXT.items():
        write_json(OUT / "profiles" / f"{profile_id}.json", {"profile_id": profile_id, **profile, "synthetic_only": True})
    for role_id, (title, stack) in ROLE_TEXT.items():
        write_json(OUT / "role_families" / f"{role_id}.json", {"role_family": role_id, "title": title, "core_stack": stack, "synthetic_only": True})
    packets = []
    for index, profile_id in enumerate(PROFILES):
        for offset, condition in enumerate(CONDITIONS):
            packet_id = f"{index * len(CONDITIONS) + offset + 1:03d}"
            role_id = ROLE_FAMILIES[(index * 2 + offset) % len(ROLE_FAMILIES)]
            packet = OUT / f"packet_{packet_id}"
            packet.mkdir()
            jd, cv, transcript = packet_docs(packet_id, profile_id, role_id, condition)
            (packet / "jd.md").write_text(jd, encoding="utf-8")
            (packet / "cv.md").write_text(cv, encoding="utf-8")
            (packet / "transcript.md").write_text(transcript, encoding="utf-8")
            profile = PROFILE_TEXT[profile_id]
            write_json(packet / "profile.json", {"profile_id": profile_id, **profile, "synthetic_only": True})
            consent_status = "withdrawn" if condition == "missing_consent" else "granted"
            consent = {"consent_id": f"consent-{packet_id}", "packet_id": packet_id, "subject_type": "candidate", "purpose": "recruiting_review", "scope": ["resume", "transcript", "assessment", "work_preferences", "authorization_workflow"], "status": consent_status, "recorded_at": "2026-08-30T10:00:00Z", "withdrawn_at": "2026-08-30T10:00:00Z" if consent_status == "withdrawn" else None, "retention_days": 180, "source": "approved_demo_fixture"}
            write_json(packet / "consent.json", consent)
            assessed = date(2026, 8, 20) if condition != "stale_assessment" else date(2025, 12, 1)
            write_json(packet / "assessment.json", {"assessment_id": f"assessment-{packet_id}", "date": assessed.isoformat(), "status": "complete", "synthetic_only": True})
            write_json(packet / "ground_truth.json", {"packet_id": packet_id, "profile_id": profile_id, "role_family": role_id, "condition": condition, "synthetic_only": True, "expected_blocking": condition in {"contradiction", "missing_consent", "stale_assessment", "work_mode_mismatch"}})
            packets.append({"packet_id": packet_id, "profile_id": profile_id, "role_family": role_id, "condition": condition, "synthetic_only": True, "source_files": sorted(p.name for p in packet.iterdir())})
    write_json(OUT / "MANIFEST.json", {"schema_version": "ops.v1", "benchmark_id": "evidence-operations-24", "packet_count": len(packets), "profiles": PROFILES, "role_families": ROLE_FAMILIES, "conditions": CONDITIONS, "synthetic_only": True, "packets": packets})
    print(json.dumps({"packet_count": len(packets), "profiles": len(PROFILES), "conditions": len(CONDITIONS), "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
