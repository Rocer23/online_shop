import datetime
import sqlite3
from fastapi import FastAPI, HTTPException, status

app = FastAPI()


def init_db():
    with sqlite3.connect("data.db") as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL
            );
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            );
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                order_date DATE NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
        ''')


init_db()


@app.put('/product/')
def create_product(name: str, category: str, price: int):
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT into products (name, category, price) VALUES (?, ?, ?)", [name, category, price])
        conn.commit()
        return {'name': name, "category": category, "price": price}


@app.put('/customers/')
def add_customer(first_name: str, last_name: str, email: str):
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT into customers (first_name, last_name, email) VALUES (?, ?, ?)",
                       [first_name, last_name, email])
        conn.commit()
        return {"first_name": first_name, "last_name": last_name, "email": email}


@app.put('/order/')
def create_order(customer_id: int, product_id: int, quantity: int, order_date: str):
    try:
        order_date_parsed = datetime.datetime.strptime(order_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid order date")

    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT into orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)",
                       [customer_id, product_id, quantity, order_date_parsed])
        conn.commit()
        return {"customer_id": customer_id,
                "product_id": product_id,
                "quantity": quantity,
                "order_date": str(order_date_parsed)
                }
