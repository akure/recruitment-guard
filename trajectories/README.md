# Agent trajectories

The guarded runner writes one JSON file per packet as `packet_NN.json`. Each trajectory records the structured extraction output, deterministic validator findings, checkpoint state and resolution notes, the final brief path, model-call token usage, and elapsed runtime.

A packet with blocking findings ends in `pending_review` and has no final brief path until a recruiter resolution is recorded. A clean packet finalizes directly. A reviewed packet changes to `finalized` only through the same finalization gate used by the CLI.

The committed examples are representative artifacts for the judge: packet 03 demonstrates a missing-evidence pause, and packet 04 demonstrates a clean direct finalization. Reproduction runs may generate additional packet trajectories in this directory.
