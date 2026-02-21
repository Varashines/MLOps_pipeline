from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, ValidationError


class SalesRow(BaseModel):
    # 1. Handling Aliases (CSV Header -> Python Name)
    # The CSV column is "Transaction Date", but we want 'txn_date'
    txn_date: date = Field(alias="Transaction Date")

    # 2. Constraints (Field)
    # Price must be strictly positive (>0)
    price: float = Field(gt=0, alias="Unit Price")

    # Quantity must be at least 1. If missing, default to 1.
    quantity: int = Field(default=1, ge=1, alias="Qty")

    # 3. Optional Fields
    # Discount might be missing (None). That's okay.
    discount: Optional[float] = Field(default=None)


# --- SIMULATION ---

# Scenario: A row from a Pandas DataFrame or CSV
# Note the "messy" format:
# - Date is a string
# - Price is a string with whitespace
# - Discount is missing entirely
raw_csv_row = {
    "Transaction Date": "2025-10-01",
    "Unit Price": "  1500.50  ",  # Messy string with spaces
    "Qty": 5,
    # "Discount" is missing
}

try:
    # We use by_alias=True because input keys match the aliases
    clean_row = SalesRow.model_validate(raw_csv_row)

    print("✅ DATA CLEANED SUCCESSFULLY")
    print(f"Date Object: {clean_row.txn_date} (Type: {type(clean_row.txn_date)})")
    print(f"Price: {clean_row.price}")
    print(f"Discount: {clean_row.discount}")  # It handled the missing value

except ValidationError as e:
    print(e)

# --- FAILURE TEST ---
print("\n--- Testing Bad Data ---")
bad_row = {
    "Transaction Date": "Not-a-date",
    "Unit Price": -50,  # Negative price (Field(gt=0) should catch this)
    "Qty": 0,
}

try:
    SalesRow.model_validate(bad_row)
except ValidationError as e:
    print("❌ Pydantic blocked the bad data:")
    # We iterate over errors to see how clear they are
    for err in e.errors():
        print(f"- Field: {err['loc']}, Msg: {err['msg']}")
