---
trigger: model_decision
description: "Apply these evidence rules for Labeeb runtime probes, discovery, audits, release criteria, and any claim that behavior works or fails."
---

# Labeeb Evidence Invariants

1. Direct runtime observation outranks repository interpretation for observed behavior.
2. A verdict cannot cover a boundary that was not observed on the proof path.
3. Historical records prove historical state only; they do not prove a fresh execution works now.
4. Preserve a stable identity across boundaries whenever possible: request/session/article/job/document ID, canonical URL, or equivalent. It must come from an observed runtime identifier; never invent one from a date, label, or expected name.
5. Preserve path fidelity. A downstream synthetic shortcut proves only that downstream slice unless the original question is explicitly downstream-only.
6. Resolve one evidenced canonical entrypoint before running a decisive experiment. If entrypoint identity remains ambiguous, report `UNKNOWN` rather than inventing alternatives.
7. Separate `Observed fact`, `Inference`, `Unknown`, and `Knowledge gap`.
8. A product/release finding requires expected behavior + direct observed mismatch + explicit impact.
9. Stop broad research at the first trustworthy material answer or first proven failure boundary.
10. Distinguish capability proof, release-criterion proof, and complete release-journey proof.
11. Deployed identity matters: repository SHA alone does not prove what production is running.
12. Never persist secrets, bearer tokens, passwords, or credentials in reports, prompts, memory, or agent messages.
