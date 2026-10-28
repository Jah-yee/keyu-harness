# Validation Report

**Result: PASS**

- Editable package installation: `PASS`
- Unit tests: `PASS` (23 test-output lines)
- Source registry validation: `PASS`
- Claim ledger + source cross-reference validation: `PASS`
- Artifact registry + source cross-reference validation: `PASS`
- Synthetic demos: `PASS`
- Python compile check: `PASS`
- BibTeX brace balance: `PASS`
- Unique IDs: source=26, claims=16, artifacts=12

## Unit tests

```text
Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/spreadsheet_warmup.py", line 718, in _warm_feature_flows
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/spreadsheet_warmup.py", line 509, in _warm_drawing_and_image_flows
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/generated/interface/models.py", line 32861, in bring_to_front
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/rpc/remote.py", line 764, in __call__
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/rpc/client.py", line 175, in call
artifact_tool.rpc.client.RemoteError: Element ordering requires an owning element collection.
test_artifact_registry_validates (test_simulator.SimulatorTests.test_artifact_registry_validates) ... ok
test_artifact_source_ids_resolve (test_simulator.SimulatorTests.test_artifact_source_ids_resolve) ... ok
test_claim_ledger_validates (test_simulator.SimulatorTests.test_claim_ledger_validates) ... ok
test_claim_source_ids_resolve (test_simulator.SimulatorTests.test_claim_source_ids_resolve) ... ok
test_source_registry_validates (test_simulator.SimulatorTests.test_source_registry_validates) ... ok
test_t5_mismatch_is_flagged_as_synthetic (test_simulator.SimulatorTests.test_t5_mismatch_is_flagged_as_synthetic) ... ok
test_trace_outliers_are_flagged (test_simulator.SimulatorTests.test_trace_outliers_are_flagged) ... ok
test_unmarked_scenario_is_rejected (test_simulator.SimulatorTests.test_unmarked_scenario_is_rejected) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.003s

OK

```

## Ledger checks

```text
SOURCE: {"valid": true, "kind": "sources", "path": "references/source_registry.csv"}
CLAIMS: {"valid": true, "kind": "claims", "path": "references/claim_ledger.csv"}
ARTIFACTS: {"valid": true, "kind": "artifacts", "path": "references/artifact_registry.csv"}
```

## Synthetic demo

```text
{
  "scenario_id": "SIM-T5-001",
  "findings": 1,
  "status": "synthetic_metadata_inconsistency_detected",
  "output": "/mnt/data/Downloads/Keyu_Harness/outputs/t5-demo"
}
{
  "scenario_id": "SIM-TRACE-001",
  "findings": 2,
  "status": "synthetic_metric_outliers_detected",
  "output": "/mnt/data/Downloads/Keyu_Harness/outputs/trace-demo"
}
Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/spreadsheet_warmup.py", line 718, in _warm_feature_flows
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/spreadsheet_warmup.py", line 509, in _warm_drawing_and_image_flows
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/generated/interface/models.py", line 32861, in bring_to_front
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/rpc/remote.py", line 764, in __call__
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/rpc/client.py", line 175, in call
artifact_tool.rpc.client.RemoteError: Element ordering requires an owning element collection.

```

## Interpretation

A passing check validates the current research tooling and synthetic fixtures only. It does not establish historical incident facts or causality. Public references with empty `sha256` and `local_path` fields have not been captured as local files.
