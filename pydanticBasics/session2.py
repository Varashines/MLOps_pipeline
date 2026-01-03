from pydantic import BaseModel, ValidationError, field_validator


class StoreLocation(BaseModel):
    store_id: int
    state: str

    # CUSTOM RULE: We only operate in South India for this project
    @field_validator("state")
    @classmethod
    def must_be_south_india(cls, v: str) -> str:
        # Standardize input (handle 'karnataka' vs 'Karnataka')
        value = v.title()

        allowed_states = [
            "Karnataka",
            "Tamil Nadu",
            "Kerala",
            "Telangana",
            "Andhra Pradesh",
        ]

        if value not in allowed_states:
            raise ValueError(f"We do not operate in {value}. Allowed: {allowed_states}")

        return value


# --- TEST ---
try:
    # 1. Good Case (Note lowercase 'karnataka' gets fixed)
    loc = StoreLocation(store_id=101, state="karnataka")
    print(f"✅ Accepted: {loc.state}")

    # 2. Bad Case
    loc_fail = StoreLocation(store_id=102, state="Delhi")
except ValidationError as e:
    print(f"❌ Rejected: {e}")
