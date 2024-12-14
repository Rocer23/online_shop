import datetime
import sqlite3
from fastapi import FastAPI, HTTPException, status
import uvicorn

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


@app.post('/products/')
def create_product(name: str, category: str, price: int):
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT into products (name, category, price) VALUES (?, ?, ?)", [name, category, price])
        conn.commit()
        return {'name': name, "category": category, "price": price}


@app.post('/customers/')
def add_customer(first_name: str, last_name: str, email: str):
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT into customers (first_name, last_name, email) VALUES (?, ?, ?)",
                       [first_name, last_name, email])
        conn.commit()
        return {"first_name": first_name, "last_name": last_name, "email": email}


@app.post('/order/')
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


@app.get('/orders/')
def show_all_orders():
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.order_id, c.first_name, c.last_name, p.name, p.category, p.price, o.quantity, o.order_date 
            FROM orders o 
            JOIN customers c ON o.customer_id = c.customer_id 
            JOIN products p ON o.product_id = p.product_id
            ''')
        orders = cursor.fetchall()

        if not orders:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orders not found")

        all_orders = [
            {
                "order_id": row[0],
                "customer_id": {
                    "first_name": row[1],
                    "last_name": row[2]
                },
                "product": {
                    "name": row[3],
                    "category": row[4],
                    "price": row[5]
                },
                "quantity": row[6],
                "order_date": row[7]
            } for row in orders
        ]
        return all_orders


@app.get("/products/")
def get_all_products():
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

        all_products = [{'product_id': row[0], 'name': row[1], 'category': row[2], 'price': row[3]} for row in products]

        if not all_products:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Products not found")

        return all_products


@app.get("/customers/")
def get_all_customers():
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()

        all_customers = [{'customer_id': row[0], 'first_name': row[1], "last_name": row[2], "email": row[3]}
                         for row in customers]

        if not all_customers:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customers not found")

        return all_customers


@app.get("/customer/")
def get_customer_by_id(customer_id: str):
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE customer_id = ?", [customer_id])
        customer = cursor.fetchone()

        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        return {"customer_id": customer[0], "first_name": customer[1], "last_name": customer[2], "email": customer[3]}


@app.delete('/products/')
def delete_product(product_id):
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM products WHERE product_id = ?''', [product_id])
        conn.commit()
        return {'message': "Product deleted successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
