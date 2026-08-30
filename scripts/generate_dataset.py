from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
JD = """Role: **Backend Engineer**, Series B fintech startup.

Core requirements:
- 3+ years backend experience
- Go or Python
- Distributed systems exposure
- Comfort owning a service end-to-end
- Payments or financial-systems domain is a plus, not required
"""

CLEAN = [
    ("01", "Mira", "4 years", "Python", "shipment ledger", "3 engineers", "2026-08-12"),
    ("02", "Jon", "5 years", "Go", "risk-events service", "4 engineers", "2026-08-14"),
    ("04", "Nia", "3 years", "Python", "account-notify service", "2 engineers", "2026-08-10"),
    ("05", "Owen", "6 years", "Go", "settlement reconciler", "5 engineers", "2026-08-11"),
    ("06", "Sana", "2 years", "Python", "merchant-config API", "1 engineer", "2026-08-09"),
    ("07", "Tariq", "7 years", "Go", "fraud-signals service", "6 engineers", "2026-08-13"),
    ("08", "Lena", "4 years", "Python", "invoice routing service", "3 engineers", "2026-08-08"),
    ("09", "Pavel", "5 years", "Go", "payouts gateway", "4 engineers", "2026-08-07"),
    ("10", "Rhea", "3 years", "Python", "identity-events API", "2 engineers", "2026-08-06"),
    ("11", "Ilan", "6 years", "Go", "treasury limits service", "5 engineers", "2026-08-05"),
    ("12", "Zoe", "4 years", "Python", "billing-notices worker", "2 engineers", "2026-08-04"),
]


def write_packet(packet_id: str, cv: str, transcript: str, assessment: dict | None) -> None:
    packet = DATA / f"packet_{packet_id}"
    packet.mkdir(parents=True, exist_ok=True)
    (packet / "jd.md").write_text(JD, encoding="utf-8")
    (packet / "cv.md").write_text(cv, encoding="utf-8")
    (packet / "transcript.md").write_text(transcript, encoding="utf-8")
    assessment_path = packet / "assessment.json"
    if assessment is None:
        assessment_path.unlink(missing_ok=True)
    else:
        assessment_path.write_text(json.dumps(assessment, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    DATA.mkdir(exist_ok=True)
    for packet_id, name, tenure, stack, project, team, date in CLEAN:
        cv = f"""# {name}'s CV\n\n- {tenure} of backend engineering experience.\n- Primary stack: {stack}; built distributed services and APIs.\n- Owned the {project} end-to-end, including design, delivery, and operations.\n- Worked with a team of {team}.\n"""
        transcript = f"""# Interview transcript — {name}\n\nInterviewer: Tell me about a service you owned.\n{name}: I owned the {project} end-to-end, from design through operations.\n\nInterviewer: What was the team structure?\n{name}: We were a team of {team}; I was responsible for the backend service.\n\nInterviewer: What is your backend experience and stack?\n{name}: I have {tenure} of backend experience and mainly use {stack}. I have worked with distributed services.\n"""
        write_packet(packet_id, cv, transcript, {"score": 78 + int(packet_id) % 10, "date": date})

    write_packet(
        "01",
        """# Vale's CV\n\n- 5 years of backend engineering experience.\n- Primary stack: Go; built distributed payment services.\n- Led a team of 8 engineers on the payments migration, owning architecture and delivery.\n- Expert in service ownership and operational readiness.\n""",
        """# Interview transcript — Vale\n\nInterviewer: Tell me about the payments migration.\nVale: Yeah, that one — honestly it was mostly me. I had code review from one senior engineer but I drove the whole thing solo.\n\nInterviewer: What did you build with?\nVale: Go, with distributed workers and careful retry handling. I have 5 years of backend experience.\n""",
        {"score": 84, "date": "2026-08-15"},
    )
    write_packet(
        "02",
        """# Keiko's CV\n\n- 4 years of backend engineering experience.\n- Expert in distributed systems — designed and operated multi-region, strongly-consistent services at scale.\n- Primary stack: Python; owned a ledger API end-to-end.\n- Worked with a team of 3 engineers.\n""",
        """# Interview transcript — Keiko\n\nInterviewer: Can you walk me through how you'd reason about consistency guarantees in a multi-region setup?\nKeiko: Uh, I mean, we just made sure the database was replicated so it was fine, I didn't really need to think about it much beyond that.\n\nInterviewer: Tell me about your recent service.\nKeiko: I owned a ledger API end-to-end with Python. I have 4 years of backend experience and worked with 3 engineers.\n""",
        {"score": 81, "date": "2026-08-14"},
    )
    write_packet(
        "03",
        """# Rowan's CV\n\n- 5 years of backend engineering experience.\n- Primary stack: Go; built distributed services.\n- Owned the account-events API end-to-end with a team of 4 engineers.\n""",
        """# Interview transcript — Rowan\n\nInterviewer: Tell me about your recent service.\nRowan: I owned the account-events API end-to-end with a team of 4 engineers.\n\nInterviewer: What is your backend experience?\nRowan: I have 5 years of backend experience and mainly use Go on distributed services.\n""",
        None,
    )


if __name__ == "__main__":
    main()
