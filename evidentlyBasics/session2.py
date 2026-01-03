import json

import numpy as np
import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

# 1. Setup Data
print("⚙️ Generating Data...")
ref_data = pd.DataFrame({"sales": np.random.normal(100, 10, 1000)})
curr_data = pd.DataFrame({"sales": np.random.normal(130, 10, 1000)})

# 2. Run Report
print("🏃 Running Drift Check...")
report = Report(metrics=[DataDriftPreset()])
results = report.run(reference_data=ref_data, current_data=curr_data)

# 3. Parse Results
data = json.loads(results.json())

drift_detected = False

# LOOP through all metrics
for metric in data.get("metrics", []):
    # TRIAGE: Check 'result' OR 'value'
    # (Your version puts it in 'value')
    payload = metric.get("result") or metric.get("value")

    if isinstance(payload, dict) and "dataset_drift" in payload:
        drift_detected = payload["dataset_drift"]
        print(
            f"✅ Found drift data in key: '{'result' if metric.get('result') else 'value'}'"
        )
        break

# 4. Result
if drift_detected:
    print("❌ PIPELINE STOPPED: Critical Drift Detected.")
else:
    print("✅ PIPELINE PROCEEDING: Data is stable.")
