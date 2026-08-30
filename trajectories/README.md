# Agent trajectories

The guarded runner writes one JSON file per packet as `packet_NN.json`. Each trajectory records the structured extraction output, deterministic validator findings, checkpoint state and resolution notes, the final brief path, model-call token usage, and elapsed runtime.

A packet with blocking findings ends in `pending_review` and has no final brief path until a recruiter resolution is recorded. A clean packet finalizes directly. A reviewed packet changes to `finalized` only through the same finalization gate used by the CLI.

The committed examples are representative artifacts for the judge: packet 03 demonstrates a missing-evidence pause, and packet 04 demonstrates a clean direct finalization. Reproduction runs may generate additional packet trajectories in this directory.

For an annotated end-to-end account of the agent instructions, tool/system responses, feedback loops, retries, live citation failure, and human checkpoints, read [`AGENT-TRAJECTORIES.md`](AGENT-TRAJECTORIES.md). It covers the baseline summarizer, guarded agent, v2.1 Evidence Operations workflow, and the bounded live-model retry path.
