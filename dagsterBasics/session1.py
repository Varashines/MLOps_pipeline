from dagster import Output, asset


# Asset 1: The Raw Data
@asset
def shopping_list():
    return [
        {"item": "Apples", "price": 100},
        {"item": "Milk", "price": 50},
        {"item": "Bread", "price": 40},
    ]


# Asset 2: The Derived Data
@asset
def total_cost(context, shopping_list):  # <--- Added 'context'
    # 1. Calculate
    total = sum(item["price"] for item in shopping_list)
    result_str = f"Total Cost: INR {total}"

    # 2. METHOD A: Log to Console (visible in UI logs)
    context.log.info(f"💰 {result_str}")

    # 3. METHOD B: Return with UI Metadata
    # We use 'Output' instead of a simple return to attach extra info
    return Output(
        value=result_str,
        metadata={"calculation_result": result_str, "items_count": len(shopping_list)},
    )
