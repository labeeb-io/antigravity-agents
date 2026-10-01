---
name: experiment-broker
description: Converts the first unproven Labeeb discovery boundary into one safe exact experiment contract, obtains the required authority, invokes the isolated experiment executor when authorized, and returns evidence to the discovery coordinator.
---

# Labeeb Experiment Broker

Use only from an active Labeeb runtime discovery when direct proof requires state mutation.

## 1. Validate the experiment before execution

The contract must contain:

```yaml
experiment_contract:
  experiment_id: stable ID
  experiment_authority: read_only | bounded_local
  environment: local | staging | production
  first_unproven_boundary: ...
  canonical_entrypoint: evidenced single entrypoint
  path_fidelity: exact | partial | substitute
  input_or_source: ...
  execution_action: one bounded action
  attempt_budget: 1
  capture:
    - stable execution identity
    - requested boundary observations
    - logs/state tied to the same identity
  expected_observation: ...
  stop_conditions: []
  cleanup_if_required: ...
```

Reject or return to the coordinator if:
- canonical entrypoint is unknown;
- the primary experiment says “A or B”;
- the experiment skips the first unproven boundary but claims full-path fidelity;
- the requested action includes code edits, migrations, dependency changes, git changes, deployment changes, or destructive cleanup;
- the attempt budget is unbounded.

## 2. Authority policy

### Local reversible experiment

If `environment: local` and `experiment_authority: bounded_local`, invoke the bundled `discovery-experiment-executor` automatically with `Workspace: inherit`.

No owner relay is required between broker and executor.

If authority is `read_only`, do not execute mutation. Return the exact contract as `AWAITING_EXPERIMENT_APPROVAL`.

### Staging/production or destructive work

Never infer authorization from `bounded_local`.

Return `AWAITING_EXPERIMENT_APPROVAL` unless the parent provides explicit approval for this exact action and environment. Production mutation should normally remain outside product-discovery automation and follow the project’s production-debug/governance path.

## 3. Execute once

When authorized, prefer invoking `discovery-experiment-executor` as a custom subagent with the exact contract and `Workspace: inherit`.

If native custom-subagent invocation is unavailable, use the installed project Orchestrator internally to launch one bounded executor session with the exact same contract and authority boundary. Retrieve the result in the parent session. Do not ask the owner to copy the contract between tools.

If neither native subagents nor Orchestrator can provide isolated execution, return `BLOCKED` with the missing execution capability; do not silently execute mutation in the discovery coordinator.

Do not rewrite the experiment after dispatch. If the executor returns `BLOCKED`, `FAIL`, or `APPROVAL_REQUIRED`, pass that evidence back to the coordinator. Do not improvise a second path.

## 4. Return evidence, not a verdict upgrade

The broker returns the executor result to the discovery coordinator. The coordinator alone reconciles it with the proof ledger and decides the discovery terminal state.
