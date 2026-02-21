from typing import List

from pydantic import BaseModel, Field, ValidationError, model_validator


# --- CHILD MODEL ---
class OrderItem(BaseModel):
    name: str
    price: float = Field(gt=0)
    quantity: int = Field(gt=0)
    discount: float = Field(default=0.0, ge=0.0)

    # CROSS-FIELD VALIDATOR
    @model_validator(mode="after")
    def check_discount(self):
        if self.price is not None and self.discount > self.price:
            raise ValueError("Discount cannot exceed the item price")
        return self

    # Helper property (not a field, just logic)
    @property
    def subtotal(self):
        return (self.price - self.discount) * self.quantity


# --- PARENT MODEL ---
class Order(BaseModel):
    order_id: str
    # Nesting: An Order has a list of OrderItems
    items: List[OrderItem]

    # The total claimed by the frontend API
    declared_total: float

    # CROSS-FIELD VALIDATOR
    @model_validator(mode="after")
    def verify_total(self):
        # 1. Calculate the REAL total from the items
        calculated_total = sum(item.subtotal for item in self.items)

        # 2. Compare with the declared total
        # (Use a small epsilon for float comparison safety)
        if abs(calculated_total - self.declared_total) > 0.01:
            raise ValueError(
                f"Total Mismatch! Items sum to {calculated_total}, "
                f"but declared total is {self.declared_total}"
            )
        return self


# --- SIMULATION ---

# Scenario: Frontend sends a "Buggy" request
bad_payload = {
    "order_id": "ORD-555",
    "declared_total": 500.0,  # CLAIM: 500
    "items": [
        {"name": "Mouse", "price": 100.0, "quantity": 2, "discount": 20},  # 200
        {"name": "Keyboard", "price": 500.0, "quantity": 1},  # 500 -> Real Total: 700
    ],
}

print("--- Validating Order ---")
try:
    order = Order(**bad_payload)
    print("✅ Order Validated")
except ValidationError as e:
    print("❌ FRAUD DETECTED:")
    # Pretty printing the specific error message
    for err in e.errors():
        print(f"- {err['msg']}")

# Scenario: Correct Request
good_payload = bad_payload.copy()
good_payload["declared_total"] = 660.0  # Fix the total

try:
    order = Order(**good_payload)
    print(f"\n✅ Fixed Order Accepted. Total items: {len(order.items)}")
except ValidationError as e:
    print("Should not fail\n" + str(e))
