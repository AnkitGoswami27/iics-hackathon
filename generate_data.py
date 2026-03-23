import pandas as pd
import random
from faker import Faker

fake = Faker()

data = []

for i in range(500000):
    quantity = random.randint(1,5)
    price = random.randint(500,5000)
    discount = random.randint(0,200)
    total = quantity * price
    final = total - discount

    data.append([
        f"ORD{100000+i}",
        fake.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d'),
        f"CUST{random.randint(100,500)}",
        f"PROD{random.randint(500,550)}",
        f"STR{random.randint(1,10)}",
        quantity,
        price,
        discount,
        total,
        final,
        random.choice(["SUCCESS","FAILED","PENDING"]),
        random.choice(["UPI","CARD","COD"]),
        fake.city(),
        fake.state(),
        random.choice(["North","South","East","West"])
    ])

df = pd.DataFrame(data, columns=[
"order_id","order_date","customer_id","product_id","store_id",
"quantity","selling_price","discount","total_amount","final_amount",
"payment_status","payment_mode","city","state","region"
])

df.to_csv("retail_500k.csv", index=False)