import numpy as np
import pandas as pd
from evidently import Report  # Changed import to be explicit
from evidently.presets import DataDriftPreset

# 1. Simulate Data
ref_data = pd.DataFrame({"sales": np.random.normal(50, 10, 1000)})
curr_data = pd.DataFrame({"sales": np.random.normal(70, 10, 1000)})

print("📊 Analyzing Data...")

# 2. Configure the Report
report_config = Report(metrics=[DataDriftPreset()])

# 3. Run & CAPTURE THE RESULT (Critical Change)
report_result = report_config.run(reference_data=ref_data, current_data=curr_data)

# 4. Save the RESULT
output_file = "drift_report.html"
report_result.save_html(output_file)  # Call save_html on the result, not the config

print(f"✅ Report saved to '{output_file}'. Open this file in your browser!")
