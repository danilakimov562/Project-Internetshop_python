#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import sqlite3
from sqlite3 import Connection
from typing import List, Optional
from models import Client, Product, Order
from datetime import datetime
import json
import csv
import os

DB_NAME = "shop.db"

class Database:
    """Класс для работы с SQLite базой данных интернет-магазина"""
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self.conn: Optional[Connection] = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Устанавливает соединение с базой данных SQLite."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")

    def close(self):
        """Закрывает соединение с базой данных."""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Создаёт таблицы clients, products, orders и order_products, если их нет."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    client_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY,
                    client_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(client_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_products (
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(order_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id),
                    PRIMARY KEY (order_id, product_id)
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблиц: {e}")

    def add_client(self, client: Client) -> bool:
        """Добавляет клиента в базу."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO clients (client_id, name, email, phone)
                VALUES (?, ?, ?, ?)
            """, (client.client_id, client.name, client.email, client.phone))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Клиент с client_id={client.client_id} уже существует.")
            return False
        except sqlite3.Error as e:
            print(f"Ошибка добавления клиента: {e}")
            return False

    def get_client(self, client_id: int) -> Optional[Client]:
        """Получает клиента по ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM clients WHERE client_id = ?", (client_id,))
            row = cursor.fetchone()
            if row:
                return Client(row["client_id"], row["name"], row["email"], row["phone"])
            return None
        except sqlite3.Error as e:
            print(f"Ошибка получения клиента: {e}")
            return None

    def get_all_clients(self) -> List[Client]:
        """Получает список всех клиентов."""

        clients = []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM clients")
            rows = cursor.fetchall()
            for row in rows:
                clients.append(Client(row["client_id"], row["name"], row["email"], row["phone"]))
        except sqlite3.Error as e:
            print(f"Ошибка получения клиентов: {e}")
        return clients

    def delete_client(self, client_id: int) -> bool:
        """Удаляет клиента и связанные с ним заказы."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT order_id FROM orders WHERE client_id = ?", (client_id,))
            order_ids = [row["order_id"] for row in cursor.fetchall()]
            for oid in order_ids:
                cursor.execute("DELETE FROM order_products WHERE order_id = ?", (oid,))
            cursor.execute("DELETE FROM orders WHERE client_id = ?", (client_id,))
            cursor.execute("DELETE FROM clients WHERE client_id = ?", (client_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при удалении клиента: {e}")
            return False

    def add_product(self, product: Product) -> bool:
        """Добавляет товар в базу."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO products (product_id, name, price)
                VALUES (?, ?, ?)
            """, (product.product_id, product.name, product.price))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Товар с product_id={product.product_id} уже существует.")
            return False
        except sqlite3.Error as e:
            print(f"Ошибка добавления товара: {e}")
            return False

    def get_product(self, product_id: int) -> Optional[Product]:
        """Получает товар по ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            row = cursor.fetchone()
            if row:
                return Product(row["product_id"], row["name"], row["price"])
            return None
        except sqlite3.Error as e:
            print(f"Ошибка получения товара: {e}")
            return None

    def get_all_products(self) -> List[Product]:
        """Получает список всех товаров."""
        products = []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM products")
            rows = cursor.fetchall()
            for row in rows:
                products.append(Product(row["product_id"], row["name"], row["price"]))
        except sqlite3.Error as e:
            print(f"Ошибка получения товаров: {e}")
        return products

    def delete_product(self, product_id: int) -> bool:
        """Удаляет товар и связанные с ним записи в заказах."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM order_products WHERE product_id = ?", (product_id,))
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при удалении товара: {e}")
            return False

    def add_order(self, order: Order) -> bool:
        """Добавляет заказ с товарами в базу."""

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO orders (order_id, client_id, date, status)
                VALUES (?, ?, ?, ?)
            """, (order.order_id, order.client.client_id, order.date.isoformat(), order.status))
            for product in order.products:
                cursor.execute("""
                    INSERT INTO order_products (order_id, product_id)
                    VALUES (?, ?)
                """, (order.order_id, product.product_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Заказ с order_id={order.order_id} уже существует.")
            return False
        except sqlite3.Error as e:
            print(f"Ошибка добавления заказа: {e}")
            return False

    def get_order(self, order_id: int) -> Optional[Order]:
        """Получает заказ по ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            order_row = cursor.fetchone()
            if not order_row:
                return None
            client = self.get_client(order_row["client_id"])
            cursor.execute("SELECT p.product_id, p.name, p.price FROM products p "
                           "JOIN order_products op ON p.product_id = op.product_id "
                           "WHERE op.order_id = ?", (order_id,))
            products_rows = cursor.fetchall()
            products = [Product(row["product_id"], row["name"], row["price"]) for row in products_rows]
            date = datetime.fromisoformat(order_row["date"])
            status = order_row["status"]
            return Order(order_row["order_id"], client, products, date, status)
        except sqlite3.Error as e:
            print(f"Ошибка получения заказа: {e}")
            return None

    def get_all_orders(self) -> List[Order]:
        orders = []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT order_id FROM orders")
            order_ids = [row["order_id"] for row in cursor.fetchall()]
            for oid in order_ids:
                order = self.get_order(oid)
                if order:
                    orders.append(order)
        except sqlite3.Error as e:
            print(f"Ошибка получения заказов: {e}")
        return orders

    def delete_order(self, order_id: int) -> bool:
        """Удаляет заказ и связанные товары."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM order_products WHERE order_id = ?", (order_id,))
            cursor.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка при удалении заказа: {e}")
            return False

    def get_all_orders_sorted(self, sort_by: str = "date", descending: bool = True) -> List[Order]:
        """Получить все заказы, отсортированные по дате или стоимости"""
        orders = []
        valid_sort_fields = {"date", "total"}
        if sort_by not in valid_sort_fields:
            sort_by = "date"

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT order_id FROM orders")
            order_ids = [row["order_id"] for row in cursor.fetchall()]
            orders_unsorted = []
            for oid in order_ids:
                order = self.get_order(oid)
                if order:
                    orders_unsorted.append(order)

            if sort_by == "date":
                orders = sorted(orders_unsorted, key=lambda o: o.date, reverse=descending)
            elif sort_by == "total":
                orders = sorted(orders_unsorted, key=lambda o: o.total_price(), reverse=descending)

        except sqlite3.Error as e:
            print(f"Ошибка получения заказов: {e}")

        return orders

    def export_clients_to_csv(self, filepath: str) -> None:
        """Экспортирует клиентов в CSV файл."""
        clients = self.get_all_clients()
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["client_id", "name", "email", "phone"])
            for c in clients:
                writer.writerow([c.client_id, c.name, c.email, c.phone])

    def import_clients_from_csv(self, filepath: str) -> None:
        """Импортирует клиентов из CSV файла."""
        if not os.path.exists(filepath):
            print(f"Файл {filepath} не найден.")
            return
        with open(filepath, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                client = Client(int(row["client_id"]), row["name"], row["email"], row["phone"])
                self.add_client(client)

    def export_products_to_json(self, filepath: str) -> None:
        """Экспортирует товары в JSON файл."""
        products = self.get_all_products()
        products_data = [{"product_id": p.product_id, "name": p.name, "price": p.price} for p in products]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(products_data, f, ensure_ascii=False, indent=4)

    def import_products_from_json(self, filepath: str) -> None:
        """Импортирует товары из JSON файла."""
        if not os.path.exists(filepath):
            print(f"Файл {filepath} не найден.")
            return
        with open(filepath, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
            for item in products_data:
                product = Product(item["product_id"], item["name"], item["price"])
                self.add_product(product)



