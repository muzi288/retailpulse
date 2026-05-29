import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import random
import uuid
import os

fake = Faker()

STORE_IDS = ["STORE_001", "STORE_002", "STORE_003"]
PAYMENT_METHODS = ["cash", "card", "mobile_money"]

PRODUCTS = [
    {"product_id": "SKU_001", "product_name": "Maize Meal 10kg", "unit_price": 12.99},
    {"product_id": "SKU_002", "product_name": "Cooking Oil 2L", "unit_price": 8.49},
    {"product_id": "SKU_003", "product_name": "Rice 5kg", "unit_price": 9.99},
    {"product_id": "SKU_004", "product_name": "Sugar 2kg", "unit_price": 4.99},
    {"product_id": "SKU_005", "product_name": "Bread Loaf", "unit_price": 2.49},
    {"product_id": "SKU_006", "product_name": "Milk 1L", "unit_price": 1.99},
    {"product_id": "SKU_007", "product_name": "Eggs 6 pack", "unit_price": 3.49},
    {"product_id": "SKU_008", "product_name": "Chicken 1kg", "unit_price": 6.99},
]


def generate_transactions(date: datetime) -> pd.DataFrame:
    num_transactions = random.randint(50, 200)
    records = []

    for _ in range(num_transactions):
        transaction_id = str(uuid.uuid4())
        store_id = random.choice(STORE_IDS)
        customer_id = f"CUST_{random.randint(1000, 9999)}"
        payment_method = random.choice(PAYMENT_METHODS)
        transaction_time = fake.date_time_between(
            start_date=date.replace(hour=0, minute=0, second=0),
            end_date=date.replace(hour=23, minute=59, second=59)
        ).isoformat()

        # Each transaction has 1-5 line items, no duplicate products
        num_items = random.randint(1, 5)
        basket = random.sample(PRODUCTS, num_items)

        # PASS 1: calculate all line totals and basket total first
        basket_items = []
        transaction_total = 0

        for product in basket:
            quantity = random.randint(1, 10)
            discount = round(random.uniform(0, 1.50), 2)
            line_total = round((quantity * product["unit_price"]) - discount, 2)
            transaction_total += line_total
            basket_items.append({
                "product": product,
                "quantity": quantity,
                "discount": discount,
                "line_total": line_total
            })

        transaction_total = round(transaction_total, 2)

        # PASS 2: write rows now that transaction_total is final
        for idx, item in enumerate(basket_items):
            records.append({
                "transaction_id": transaction_id,
                "line_item_id": f"{transaction_id}_LI_{idx + 1:03d}",
                "store_id": store_id,
                "customer_id": customer_id,
                "product_id": item["product"]["product_id"],
                "product_name": item["product"]["product_name"],
                "quantity": item["quantity"],
                "unit_price": item["product"]["unit_price"],
                "discount_applied": item["discount"],
                "line_total": item["line_total"],
                "transaction_total": transaction_total,
                "payment_method": payment_method,
                "transaction_time": transaction_time,
            })

    return pd.DataFrame(records)


def save_csv(df: pd.DataFrame, date: datetime):
    date_str = date.strftime("%Y-%m-%d")
    output_dir = f"output/{date_str}"
    os.makedirs(output_dir, exist_ok=True)
    filepath = f"{output_dir}/pos_transactions_{date_str}.csv"
    df.to_csv(filepath, index=False)
    print(f"Generated {len(df)} transactions → {filepath}")


if __name__ == "__main__":
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        df = generate_transactions(date)
        save_csv(df, date)
