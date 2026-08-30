# Problem Statement — Single-Role Candidate Evidence Brief

## Who has this problem

Priya is a recruiter at a Series B fintech startup. She's closing a **Backend
Engineer** req that's been open six weeks. Today she's screening candidate
#7: a job description, a résumé, and a 45-minute interview transcript. Her
hiring manager wants a briefing by end of day, and there are five more
candidates behind this one in the pipeline this week.

Priya isn't the decision-maker — she's the person who has to *build the
case* the hiring manager will actually read. That's the job this project is
built for.

## The bottleneck, in practice

Priya reads three documents that were never designed to agree with each
other:

- The **CV** is written by the candidate, in the candidate's own words, to
  present themselves favorably.
- The **interview transcript** is a live, unscripted conversation where
  details come out that were compressed or omitted on the CV.
- The **assessment score**, if there is one, was run by someone else, at
  some earlier point, and may already be stale by the time Priya reads it.

When she reviews these in isolation — CV first, then transcript, then
score — small inconsistencies are easy to miss under time pressure: a "led
a team of 8" on the CV versus "I mostly worked solo on that" in the
interview; a claimed skill that never comes up when the interviewer probes
it; an assessment score that's six months old and no longer reflects the
role the candidate is being considered for now.

None of these individually proves anything is wrong. But if Priya's
briefing quietly averages over them, the hiring manager makes a decision
on a picture that's more confident than the evidence actually supports —
and nobody registers that a contradiction was even there to resolve.

This is not a hypothetical failure mode. It's the default behavior of a
single "summarize this candidate" prompt: LLMs are good at producing a
coherent-sounding narrative even when the underlying sources don't fully
agree, because a smooth narrative is what "summarize" optimizes for.

## Why an agent — and why it needs a guard, not just a better prompt

A plain summarization agent makes this problem *worse*, not better,
because it adds a layer of confident-sounding prose on top of unresolved
contradictions. What actually helps Priya is an agent that:

1. **Only states what it can point to.** Every claim in the brief is tied
   to a specific source and a specific passage — not a paraphrase that
   quietly loses the hedge or the caveat.
2. **Surfaces disagreement instead of smoothing over it.** If the CV and
   the transcript disagree on a material point, that disagreement is the
   most important thing in the brief, not something averaged away.
3. **Refuses to complete the job when something's missing.** A stale or
   absent assessment score isn't a detail to skip past — it's a gap Priya
   needs to know about before she sends the brief upward.
4. **Never makes the call.** The agent's job stops at "here's the
   evidence, here's what's inconsistent, here's what's missing." Priya —
   and ultimately the hiring manager — makes the hire/no-hire decision. The
   agent doesn't, and structurally can't.

That last point isn't a nice-to-have. It's the design constraint the whole
system is built around: **the brief is not allowed to resolve into a
recommendation.** If it did, this would be exactly the kind of solution
the hackathon's own ground rules ask builders to avoid — an agent making a
decision that could significantly affect a real person's outcome without a
qualified human in the loop.

## What "solved" looks like

Given the same 12 candidate packets, a guarded agent should catch every
planted contradiction and every stale/missing evidence case that a
plain summarization baseline misses or glosses over — provably, on cases
anyone can re-run from a clean checkout.
