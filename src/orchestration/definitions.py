from pathlib import Path

import dagster as dg

# Automatically loads everything (assets, sensors, schedules) in the /defs folder
defs = dg.load_from_defs_folder(project_root=Path(__file__).parent)
