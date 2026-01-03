import json
import os
import sys

import pandas as pd
from dagster import (
    DefaultSensorStatus,
    Definitions,
    Output,
    RunRequest,
    ScheduleDefinition,
    SkipReason,
    asset,
    define_asset_job,
    load_assets_from_modules,
    sensor,
)

# --- IMPORTS ---
from evidently import Report
from evidently.presets import DataDriftPreset
from pydantic import BaseModel, ValidationError


# --- 1. DEFINE SCHEMA ---
class SalesRecord(BaseModel):
    store_id: int
    amount: float


# --- ASSET 1: RAW DATA INGESTION ---
# --- ASSET 1: RAW DATA INGESTION ---
@asset
def raw_data_batch():
    return [
        {"store_id": 101, "amount": 250.0},
        {"store_id": 101, "amount": 300.0},
        {"store_id": 101, "amount": 275.0},  # <--- Added
        {"store_id": 101, "amount": "bad_data"},  # <--- Added
        {"store_id": 102, "amount": 150.0},
        {"store_id": 102, "amount": 220.0},
    ]


# --- ASSET 2: VALIDATION (Pydantic) ---
@asset
def validated_data(context, raw_data_batch):
    """
    Filters data using Pydantic.
    """
    valid_records = []
    failed_count = 0

    for record in raw_data_batch:
        try:
            valid_record = SalesRecord(**record)
            valid_records.append(valid_record.model_dump())
        except ValidationError:
            failed_count += 1

    df = pd.DataFrame(valid_records)

    context.log.info(f"✅ Validation complete. Dropped {failed_count} rows.")

    return Output(
        value=df,
        metadata={
            "valid_rows": len(df),
            "preview": df.to_dict(),  # easy to read for small data
        },
    )


# --- ASSET 3: DRIFT CHECK (Evidently) ---
@asset
def drift_report(context, validated_data):
    """
    Checks for drift using PSI and 'include_tests=True'.
    This returns explicit PASS/FAIL statuses from Evidently.
    """
    context.log.info("📊 Starting Drift Analysis...")

    reference_data = pd.DataFrame(
        {
            "store_id": [101, 101, 101, 101, 102, 102],
            "amount": [250.0, 300.0, 300, 275.0, 150.0, 220.0],
        }
    )

    # 2. Run Report with Tests Enabled
    # We use PSI (Population Stability Index) which is standard for this.
    report = Report([DataDriftPreset(method="psi")], include_tests=True)

    results = report.run(reference_data=reference_data, current_data=validated_data)

    # 3. Parse Results (The Clean Way)
    json_data = json.loads(results.json())

    failed_tests = []

    # We iterate through the 'tests' list provided by Evidently
    for test in json_data.get("tests", []):
        if test["status"] == "FAIL":
            failed_tests.append(test["name"])

    # 4. Result Logic
    if failed_tests:
        status = "⚠️ DRIFT DETECTED"
        context.log.warning(f"❌ Pipeline Blocked. Failed Tests: {failed_tests}")
    else:
        status = "✅ DATA STABLE"
        context.log.info("✅ All drift tests passed.")
        context.log.info({results.json()})

    # 5. Return Output
    return Output(
        value=status,
        metadata={
            "drift_status": status,
            "failed_count": len(failed_tests),
            "failed_test_names": str(failed_tests),
        },
    )


# 1. Define a Job
# A "Job" is just a collection of assets you want to run together.
# We tell it to select all assets in this pipeline.
daily_quality_check_job = define_asset_job(
    name="daily_quality_check_job",
    selection="*",  # Selects all assets (raw -> valid -> drift)
)

# 2. Define a Schedule
# This says: "Run 'daily_quality_check_job' every day at 9:00 AM UTC"
# Cron syntax: "Minute Hour * * *"
daily_schedule = ScheduleDefinition(
    job=daily_quality_check_job, cron_schedule="0 9 * * *", name="daily_9am_schedule"
)

# 3. The Grand Assembly
# This object tells Dagster about EVERYTHING in your project.
# Note: We use a trick to load all assets defined in the current file.

current_module = sys.modules[__name__]


@sensor(job=daily_quality_check_job)
def new_file_sensor(context):
    """
    Checks the 'incoming_data' folder for new files.
    """
    directory = "incoming_data"

    # 1. Get list of files
    if not os.path.exists(directory):
        return SkipReason(f"Directory {directory} not found")

    files = os.listdir(directory)
    if not files:
        return SkipReason("No files found")

    # 2. Check each file
    for filename in files:
        filepath = os.path.join(directory, filename)

        # We use the filename as a "Cursor" (or Tracker).
        # If we have already seen this filename, we skip it.
        # context.cursor holds the last filename we processed.
        if context.cursor and filename <= context.cursor:
            continue

        # 3. Found a new file! Trigger the job.
        context.update_cursor(filename)
        return RunRequest(
            run_key=filename,  # Unique ID for this run
            run_config={},  # We could pass the filename here if we wanted
        )

    return SkipReason("No new files found")


# --- UPDATE THE DEFINITIONS ---
defs = Definitions(
    assets=load_assets_from_modules([current_module]),
    jobs=[daily_quality_check_job],
    schedules=[daily_schedule],
    sensors=[new_file_sensor],  # <--- Added the sensor here
)
