import hashlib
import random
import uuid
from datetime import datetime, timedelta

from faker import Faker
from fastapi import FastAPI, Query

fake = Faker()
app = FastAPI(title="RetailPulse E-commerce Mock API")

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

STORE_IDS = ["STORE_001", "STORE_002", "STORE_003"]
ORDER_STATUSES = ["pending", "confirmed", "shipped", "delivered", "returned"]
DEVICE_TYPES = ["mobile", "desktop", "tablet"]
FULFILLMENT_TYPES = ["delivery", "click_and_collect"]
CITIES = ["Harare", "Bulawayo", "Mutare", "Gweru", "Kwekwe"]


def hash_email(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()


def generate_orders(date: datetime) -> list:
    num_orders = random.randint(30, 150)
    orders = []

    for _ in range(num_orders):
        order_id = str(uuid.uuid4())
        customer_id = f"CUST_{random.randint(1000, 9999)}"
        customer_email = hash_email(fake.email())
        fulfillment_type = random.choice(FULFILLMENT_TYPES)
        store_id = random.choice(STORE_IDS) if fulfillment_type == "click_and_collect" else "ONLINE_DELIVERY"
        shipping_cost = 0.00 if fulfillment_type == "click_and_collect" else round(random.uniform(2.00, 8.00), 2)
        device_type = random.choice(DEVICE_TYPES)
        order_status = random.choice(ORDER_STATUSES)
        order_time = fake.date_time_between(
            start_date=date.replace(hour=0, minute=0, second=0),
            end_date=date.replace(hour=23, minute=59, second=59)
        ).isoformat()
        city = random.choice(CITIES)

        # PASS 1: calculate line items and order total
        num_items = random.randint(1, 5)
        basket = random.sample(PRODUCTS, num_items)
        basket_items = []
        order_total = 0

        for product in basket:
            quantity = random.randint(1, 10)
            discount = round(random.uniform(0, 1.50), 2)
            line_total = round((quantity * product["unit_price"]) - discount, 2)
            order_total += line_total
            basket_items.append({
                "product": product,
                "quantity": quantity,
                "discount": discount,
                "line_total": line_total
            })

        order_total = round(order_total + shipping_cost, 2)

        # PASS 2: write line item rows
        for idx, item in enumerate(basket_items):
            orders.append({
                "order_id": order_id,
                "line_item_id": f"{order_id}_LI_{idx + 1:03d}",
                "customer_id": customer_id,
                "customer_email": customer_email,
                "delivery_address_city": city,
                "fulfillment_type": fulfillment_type,
                "store_id": store_id,
                "product_id": item["product"]["product_id"],
                "product_name": item["product"]["product_name"],
                "quantity": item["quantity"],
                "unit_price": item["product"]["unit_price"],
                "discount_applied": item["discount"],
                "line_total": item["line_total"],
                "shipping_cost": shipping_cost,
                "order_total": order_total,
                "order_status": order_status,
                "device_type": device_type,
                "order_time": order_time,
            })

    return orders


@app.get("/orders")
def get_orders(date: str = Query(default=None)):
    if date:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    else:
        target_date = datetime.now()

    orders = generate_orders(target_date)
    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "total_records": len(orders),
        "orders": orders
    }


@app.get("/health")
def health():
    return {"status": "ok"}
