"""Run bounded, synthetic evidence scenarios; no shell or external code execution."""
from pathlib import Path
import csv, json

ALLOWED_KINDS = {"artifact_identity_check", "trace_anomaly"}

def load_scenario(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("kind") not in ALLOWED_KINDS:
        raise ValueError("Unsupported scenario kind.")
    if not data.get("scenario_id") or not data.get("notice", "").startswith(("FICTIONAL", "SYNTHETIC")):
        raise ValueError("Scenario must be explicitly marked fictional/synthetic.")
    return data

def run_scenario(path: Path):
    data = load_scenario(path)
    events, findings, inputs = [], [], [path.resolve()]
    if data["kind"] == "artifact_identity_check":
        for item in data.get("artifacts", []):
            mismatch = item.get("claimed_model_id") != item.get("observed_model_id")
            dims = item.get("config_d_model_claimed") != item.get("config_d_model_observed")
            event = {
                "scenario_id": data["scenario_id"], "event_type": "artifact_identity_check",
                "artifact_id": item.get("artifact_id"), "identity_mismatch": mismatch,
                "config_dimension_mismatch": dims, "source_kind": "synthetic_fixture"
            }
            events.append(event)
            if mismatch or dims:
                findings.append({
                    "severity": "HIGH" if (mismatch and dims) else "MEDIUM",
                    "message": f"{item.get('artifact_id')}: model ID/config metadata disagree in the synthetic fixture.",
                    "artifact_id": item.get("artifact_id")
                })
        conclusion = "synthetic_metadata_inconsistency_detected" if findings else "no_mismatch_in_fixture"
    else:
        # 场景内路径相对于仓库根目录解析，避免依赖当前工作目录。
        repo_root = path.resolve().parent.parent
        csv_path = (repo_root / data["trace_csv"]).resolve()
        if not csv_path.exists():
            raise FileNotFoundError(f"Trace fixture not found: {csv_path}")
        inputs.append(csv_path)
        thresholds = data.get("thresholds", {})
        with csv_path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            loss, grad = float(row["loss"]), float(row["grad_norm"])
            flagged = loss >= float(thresholds.get("loss", 3.0)) or grad >= float(thresholds.get("grad_norm", 2.0))
            event = {
                "scenario_id": data["scenario_id"], "event_type": "trace_row",
                "run_id": row["run_id"], "step": int(row["step"]), "rank": int(row["rank"]),
                "loss": loss, "grad_norm": grad, "flagged": flagged, "source_kind": "synthetic_fixture"
            }
            events.append(event)
            if flagged:
                findings.append({
                    "severity": "MEDIUM",
                    "message": f"Outlier in synthetic trace at step {row['step']} rank {row['rank']}: loss={loss}, grad_norm={grad}.",
                    "step": int(row["step"]), "rank": int(row["rank"])
                })
        conclusion = "synthetic_metric_outliers_detected" if findings else "no_outlier_in_fixture"
    report = {
        "scenario_id": data["scenario_id"], "title": data["title"], "notice": data["notice"],
        "kind": data["kind"], "findings": findings,
        "conclusion_status": conclusion, "data_class": "SIMULATED",
        "inputs": [p.name for p in inputs],
        "limitations": [
            "All input values are synthetic.",
            "A mismatch or outlier is a triage signal, not proof of intent or causality.",
            "No real repositories, weights, internal services, or live jobs were accessed."
        ]
    }
    return report, events, inputs
