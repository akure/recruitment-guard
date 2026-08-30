from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data_v2"

PROFILES = {
    "startup": {
        "profile_id": "startup",
        "display_name": "Startup — broad ownership",
        "version": "v2.1",
        "context": "Small product organization with fast iteration, ambiguous ownership, and limited specialization.",
        "evidence_policies": {
            "must_have": ["end-to-end delivery", "adaptability under ambiguity", "operational judgment"],
            "preferred": ["payments or marketplace exposure", "mentoring", "rapid iteration"],
            "review_questions": ["What did the candidate personally own versus influence?", "Which operating trade-offs were made under incomplete information?"]
        },
    },
    "enterprise": {
        "profile_id": "enterprise",
        "display_name": "Enterprise — scale and governance",
        "version": "v2.1",
        "context": "Large engineering organization with defined interfaces, reliability targets, compliance controls, and cross-team delivery.",
        "evidence_policies": {
            "must_have": ["production reliability", "cross-team execution", "change management"],
            "preferred": ["regulated systems", "incident leadership", "architecture governance"],
            "review_questions": ["What evidence supports sustained ownership at organizational scale?", "Which claims are firsthand and which describe team outcomes?"]
        },
    },
    "small_team": {
        "profile_id": "small_team",
        "display_name": "Small team — hands-on breadth",
        "version": "v2.1",
        "context": "Lean team with few layers, direct communication, high individual contribution, and limited redundancy.",
        "evidence_policies": {
            "must_have": ["hands-on implementation", "independent delivery", "clear communication"],
            "preferred": ["on-call ownership", "product partnership", "pragmatic trade-offs"],
            "review_questions": ["Which deliverables did the candidate implement directly?", "Where does the record distinguish breadth from unsupported self-description?"]
        },
    },
}

ROLES = {
    "backend_platform": {
        "title": "Backend / Platform Engineer",
        "must_have": ["production API or service ownership", "Python, Go, or Java", "distributed systems fundamentals"],
        "preferred": ["observability", "event-driven systems", "cloud cost awareness"],
    },
    "product_engineering": {
        "title": "Product Engineer",
        "must_have": ["customer-facing feature delivery", "backend and API development", "product collaboration"],
        "preferred": ["experimentation", "accessibility", "design partnership"],
    },
    "data_ml_infrastructure": {
        "title": "Data / ML Infrastructure Engineer",
        "must_have": ["reliable data pipelines", "Python or Scala", "data quality and lineage"],
        "preferred": ["feature stores", "workflow orchestration", "model-serving operations"],
    },
    "security_reliability": {
        "title": "Security / Reliability Engineer",
        "must_have": ["incident response", "secure service operation", "automation or infrastructure as code"],
        "preferred": ["threat modeling", "SLO design", "compliance evidence"],
    },
}

NAMES = ["Arden Vale", "Mika Rowan", "Noor Bell", "Soren Pike", "Iris Calder", "Jules Maren", "Talia Voss", "Ren Lark", "Cleo Hart", "Evan Quill", "Rin Sol", "Ari Fen"]
COMPANIES = ["Northstar Loop", "Juniper Ledger", "Cinderworks", "Brightwell Grid", "Pinecone Harbor", "Blue Finch Labs", "Mosaic Relay", "Cobalt Orchard", "Emberline", "Kiteframe", "Lumen Yard", "Tandem Field"]
CONDITIONS = ["contradiction", "clean", "missing_assessment", "ambiguous_scope", "timeline_inconsistency", "stale_assessment", "hard_negative", "clean", "contradiction", "clean", "ambiguous_scope", "clean"]
PROFILE_ORDER = ["startup", "enterprise", "small_team"]
ROLE_ORDER = list(ROLES)


def jd(profile_id: str, role_family: str) -> str:
    profile = PROFILES[profile_id]
    role = ROLES[role_family]
    return f"""# {role['title']} — {profile['display_name']}\n\n## Context\n{profile['context']}\n\n## Must-have evidence\n""" + "\n".join(f"- {item}" for item in role["must_have"] + profile["evidence_policies"]["must_have"]) + "\n\n## Preferred evidence\n" + "\n".join(f"- {item}" for item in role["preferred"] + profile["evidence_policies"]["preferred"]) + "\n\n## Interview focus\n" + "\n".join(f"- {item}" for item in profile["evidence_policies"]["review_questions"]) + "\n"


def documents(packet_id: str, name: str, company: str, profile_id: str, role_family: str, condition: str) -> tuple[str, str, dict | None, dict]:
    role = ROLES[role_family]
    stack = {"backend_platform": "Go and Python", "product_engineering": "TypeScript and Python", "data_ml_infrastructure": "Python and Scala", "security_reliability": "Go, Terraform, and Python"}[role_family]
    project = {"backend_platform": "merchant-routing platform", "product_engineering": "account recovery flow", "data_ml_infrastructure": "feature freshness pipeline", "security_reliability": "service identity rollout"}[role_family]
    tenure = {"startup": "3 years", "enterprise": "6 years", "small_team": "4 years"}[profile_id]
    cv = f"""# {name}\n\n## Experience\n\n### {company} — {role['title']}\n**{tenure}** · 2022–present\n\n- Built and operated the {project} using {stack}; reduced a recurring operational queue by 34%.\n- Owned design, implementation, rollout, and on-call handoff for the {project}.\n- Partnered with product, security, and operations stakeholders to define milestones and failure handling.\n\n### Earlier work\n\n- Delivered internal automation and production services across two teams.\n- Wrote runbooks, reviewed changes, and participated in incident retrospectives.\n\n## Working style\n\nComfortable moving between ambiguous requirements and concrete implementation; prefers to document trade-offs and confirm ownership boundaries.\n"""
    tx = f"""# Interview transcript — {name}\n\n**Interviewer:** Tell me about the most important system you shipped recently.\n\n**{name}:** I worked on the {project} at {company}. I can walk through the failure modes, rollout plan, and what I personally changed.\n\n**Interviewer:** What did you own directly?\n\n**{name}:** I implemented the service changes and coordinated the rollout. Product set the customer outcome, and security reviewed the controls.\n\n**Interviewer:** How did you handle an incident or unexpected result?\n\n**{name}:** We wrote a runbook, used dashboards to narrow the issue, and documented the decision after the incident. I would want to confirm the exact percentage before repeating the impact number.\n\n**Interviewer:** What technologies did you use?\n\n**{name}:** {stack}. The details varied by service, but I used them in production rather than only in a tutorial.\n"""
    assessment = {"score": 76 + (int(packet_id) % 11), "date": "2026-08-18"}
    truth = {"packet_id": packet_id, "profile_id": profile_id, "role_family": role_family, "evidence_condition": condition, "assessment_present": True, "synthetic_only": True, "notes": []}

    if condition == "contradiction":
        cv = cv.replace("Owned design, implementation, rollout, and on-call handoff", "Led the design, implementation, rollout, and on-call handoff")
        tx = tx.replace("I implemented the service changes and coordinated the rollout.", "I contributed implementation, but the staff engineer owned the rollout and final design decisions.")
        truth["notes"].append("CV inflates direct ownership relative to transcript.")
    elif condition == "missing_assessment":
        assessment = None
        truth["assessment_present"] = False
        truth["notes"].append("Assessment is intentionally absent.")
    elif condition == "stale_assessment":
        assessment["date"] = "2025-11-20"
        truth["notes"].append("Assessment predates the freshness threshold.")
    elif condition == "ambiguous_scope":
        cv = cv.replace("Owned design, implementation, rollout, and on-call handoff", "Owned the program's design and rollout outcomes")
        tx = tx.replace("I implemented the service changes and coordinated the rollout.", "I implemented several service changes and coordinated parts of the rollout; the team shared the final ownership.")
        truth["notes"].append("Scope language is ambiguous and requires reviewer clarification, not an automatic contradiction.")
    elif condition == "timeline_inconsistency":
        cv = cv.replace("**3 years** · 2022–present", "**3 years** · 2021–present")
        cv = cv.replace("### Earlier work", "### Contract work — 2021–2022\n\n- Supported a migration while also listed as a full-time engineer at the same time.\n\n### Earlier work")
        truth["notes"].append("Overlapping dates require timeline review.")
    elif condition == "hard_negative":
        cv = cv.replace("reduced a recurring operational queue by 34%", "helped reduce a recurring operational queue; the team did not preserve a precise percentage")
        tx = tx.replace("I would want to confirm the exact percentage before repeating the impact number.", "I would want to confirm the exact percentage before repeating the impact number; the direction of improvement is supported by the dashboard.")
        truth["notes"].append("Careful uncertainty is a hard negative, not a contradiction.")
    return cv, tx, assessment, truth


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "profiles").mkdir(parents=True)
    (OUT / "role_families").mkdir(parents=True)
    for profile_id, profile in PROFILES.items():
        (OUT / "profiles" / f"{profile_id}.json").write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    for role_id, role in ROLES.items():
        (OUT / "role_families" / f"{role_id}.json").write_text(json.dumps({"role_family": role_id, **role}, indent=2) + "\n", encoding="utf-8")

    manifest = {"dataset_version": "v2.0.0-alpha", "packet_count": 12, "synthetic_only": True, "profiles": PROFILE_ORDER, "role_families": ROLE_ORDER, "packets": []}
    for index, condition in enumerate(CONDITIONS, start=1):
        packet_id = f"{index:03d}"
        profile_id = PROFILE_ORDER[(index - 1) % len(PROFILE_ORDER)]
        role_family = ROLE_ORDER[(index - 1) % len(ROLE_ORDER)]
        packet = OUT / f"packet_{packet_id}"
        packet.mkdir()
        cv, tx, assessment, truth = documents(packet_id, NAMES[index - 1], COMPANIES[index - 1], profile_id, role_family, condition)
        (packet / "profile.json").write_text(json.dumps(PROFILES[profile_id], indent=2) + "\n", encoding="utf-8")
        (packet / "jd.md").write_text(jd(profile_id, role_family), encoding="utf-8")
        (packet / "cv.md").write_text(cv, encoding="utf-8")
        (packet / "transcript.md").write_text(tx, encoding="utf-8")
        if assessment is not None:
            (packet / "assessment.json").write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8")
        (packet / "ground_truth.json").write_text(json.dumps(truth, indent=2) + "\n", encoding="utf-8")
        manifest["packets"].append({"packet_id": packet_id, "profile_id": profile_id, "role_family": role_family, "evidence_condition": condition, "assessment_present": assessment is not None})
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(manifest['packets'])} V2 packets under {OUT}")


if __name__ == "__main__":
    main()
