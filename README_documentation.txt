main.py
from gui import App

def main():
    """Точка входа в приложение"""
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()

models.py
import re
from datetime import datetime

class Person:
    """Класс для описания человека с контактными данными"""
    def __init__(self, name: str, email: str, phone: str):
        self.name = name
        self.email = email
        self.phone = phone

    def validate_email(self) -> bool:
        """Проверка корректность email"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, self.email) is not None

    def validate_phone(self) -> bool:
        """Проверяет корректность номера телефона (10-15 цифр)"""
        pattern = r'^\+?\d{10,15}$'
        return re.match(pattern, self.phone) is not None

    def str(self) -> str:
        """Возвращает строковое представление объекта"""
        return f"{self.name} (Email: {self.email}, Телефон: {self.phone})"

class Client(Person):
    """Класс клиента, который наследует Person, добавляет client_id"""
    def __init__(self, client_id: int, name: str, email: str, phone: str):
        self.client_id = client_id
        self.name = name
        self.email = email
        self.phone = phone

    def is_valid(self) -> bool:
        """Проверяет валидность почты и телефона клиента"""
        return self.validate_email() and self.validate_phone()

    def __str__(self) -> str:
        """Строковое представление клиента"""
        return f"Клиент {self.client_id}: {super().__str__()}"

class Product:
    """Класс для описания товара"""
    def __init__(self, product_id: int, name: str, price: float):
        self.product_id = product_id
        self.name = name
        self.price = price

    def str(self) -> str:
        """Строковое представление товара"""
        return f"{self.name} (ID: {self.product_id}, Цена: {self.price})"

class Order:
    """Класс заказа"""
    def __init__(self, order_id: int, client: Client, products: list[Product], date: datetime = None, status: str ="Новый"):
        self.order_id = order_id
        self.client = client
        self.products = products  
        self.date = date or datetime.now()
        self.status = status

    def total_price(self) -> float:
        """Считает общую стоимость заказа"""
        return sum(p.price for p in self.products)

    def str(self):
        """Строковое представление заказа"""
        product_list = ', '.join([p.name for p in self.products])
        return (f"Заказ {self.order_id} от {self.date.strftime('%d-%m-%Y %H:%M:%S')}\n"
                f"Клиент: {self.client.name}\n"
                f"Товары: {product_list}\n"
                f"Статус: {self.status}\n"
                f"Сумма: {self.total_price()}\n")

gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from models import Client, Product, Order
from db import Database
from datetime import datetime
from typing import List

import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from analysis import plot_top_clients_by_orders, plot_orders_dynamics, build_clients_graph, plot_clients_graph

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система учёта заказов")
        self.geometry("900x700")
        self.db = Database()
        self.create_widgets()

    def create_widgets(self):
        """ Создаёт вкладки интерфейса: Клиенты, Товары, Заказы и Аналитика."""
        tab_control = ttk.Notebook(self)
        self.client_tab = ttk.Frame(tab_control)
        self.product_tab = ttk.Frame(tab_control)
        self.order_tab = ttk.Frame(tab_control)
        self.analysis_tab = ttk.Frame(tab_control)

        tab_control.add(self.client_tab, text="Клиенты")
        tab_control.add(self.product_tab, text="Товары")
        tab_control.add(self.order_tab, text="Заказы")
        tab_control.add(self.analysis_tab, text="Аналитика")
        tab_control.pack(expand=1, fill="both")

        self.create_client_tab()
        self.create_product_tab()
        self.create_order_tab()
        self.create_analysis_tab()

   
    def create_client_tab(self):
        """Создаёт вкладку для управления клиентами: добавление, просмотр, удаление."""
        frame = self.client_tab

        form_frame = ttk.LabelFrame(frame, text="Добавить клиента")
        form_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(form_frame, text="ID клиента:").grid(row=0, column=0, sticky="e")
        self.client_id_entry = ttk.Entry(form_frame)
        self.client_id_entry.grid(row=0, column=1, sticky="w")

        ttk.Label(form_frame, text="Имя:").grid(row=1, column=0, sticky="e")
        self.client_name_entry = ttk.Entry(form_frame)
        self.client_name_entry.grid(row=1, column=1, sticky="w")

        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky="e")
        self.client_email_entry = ttk.Entry(form_frame)
        self.client_email_entry.grid(row=2, column=1, sticky="w")

        ttk.Label(form_frame, text="Телефон:").grid(row=3, column=0, sticky="e")
        self.client_phone_entry = ttk.Entry(form_frame)
        self.client_phone_entry.grid(row=3, column=1, sticky="w")

        add_btn = ttk.Button(form_frame, text="Добавить клиента", command=self.add_client)
        add_btn.grid(row=4, column=0, columnspan=2, pady=5)

        list_frame = ttk.LabelFrame(frame, text="Список клиентов")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Имя", "Email", "Телефон")
        self.client_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.client_tree.heading(col, text=col)
            self.client_tree.column(col, width=150)
        self.client_tree.pack(fill="both", expand=True)

        refresh_btn = ttk.Button(list_frame, text="Обновить список", command=self.load_clients)
        refresh_btn.pack(pady=5)

        delete_btn = ttk.Button(list_frame, text="Удалить клиента", command=self.delete_client)
        delete_btn.pack(pady=5)

        self.load_clients()

    def add_client(self):
        """Обрабатывает добавление нового клиента с валидацией данных из формы."""
        try:
            client_id = int(self.client_id_entry.get())
            name = self.client_name_entry.get().strip()
            email = self.client_email_entry.get().strip()
            phone = self.client_phone_entry.get().strip()
            client = Client(client_id, name, email, phone)
            if not client.is_valid():
                messagebox.showerror("Ошибка", "Неверный email или телефон.")
                return
            if self.db.add_client(client):
                messagebox.showinfo("Успех", "Клиент добавлен.")
                self.load_clients()
                self.clear_client_form()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить клиента. Возможно, ID уже существует.")
        except ValueError:
            messagebox.showerror("Ошибка", "ID клиента должен быть числом.")

    def load_clients(self):
        """Загружает список клиентов из базы данных и отображает в таблице."""
        for row in self.client_tree.get_children():
            self.client_tree.delete(row)
        clients = self.db.get_all_clients()
        for c in clients:
            self.client_tree.insert("", "end", values=(c.client_id, c.name, c.email, c.phone))

    def clear_client_form(self):
        self.client_id_entry.delete(0, tk.END)
        self.client_name_entry.delete(0, tk.END)
        self.client_email_entry.delete(0, tk.END)
        self.client_phone_entry.delete(0, tk.END)

    def delete_client(self):
        """Удаляет выбранного клиента из базы данных и обновляет список."""
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите клиента для удаления.")
            return
        client_id = self.client_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Подтверждение", f"Удалить клиента с ID {client_id}?"):
            if self.db.delete_client(client_id):
                messagebox.showinfo("Успех", "Клиент удалён.")
                self.load_clients()
                self.load_orders()  # Обновить заказы, т.к. могли удалиться связанные
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить клиента.")

    def create_product_tab(self):
        """Создаёт вкладку для управления товарами: добавление, просмотр, удаление."""
        frame = self.product_tab

        form_frame = ttk.LabelFrame(frame, text="Добавить товар")
        form_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(form_frame, text="ID товара:").grid(row=0, column=0, sticky="e")
        self.product_id_entry = ttk.Entry(form_frame)
        self.product_id_entry.grid(row=0, column=1, sticky="w")

        ttk.Label(form_frame, text="Название:").grid(row=1, column=0, sticky="e")
        self.product_name_entry = ttk.Entry(form_frame)
        self.product_name_entry.grid(row=1, column=1, sticky="w")

        ttk.Label(form_frame, text="Цена:").grid(row=2, column=0, sticky="e")
        self.product_price_entry = ttk.Entry(form_frame)
        self.product_price_entry.grid(row=2, column=1, sticky="w")

        add_btn = ttk.Button(form_frame, text="Добавить товар", command=self.add_product)
        add_btn.grid(row=3, column=0, columnspan=2, pady=5)

        list_frame = ttk.LabelFrame(frame, text="Список товаров")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Название", "Цена")
        self.product_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=150)
        self.product_tree.pack(fill="both", expand=True)

        refresh_btn = ttk.Button(list_frame, text="Обновить список", command=self.load_products)
        refresh_btn.pack(pady=5)

        delete_btn = ttk.Button(list_frame, text="Удалить товар", command=self.delete_product)
        delete_btn.pack(pady=5)

        self.load_products()

    def add_product(self):
        """Обрабатывает добавление нового товара с валидацией данных из формы."""
        try:
            product_id = int(self.product_id_entry.get())
            name = self.product_name_entry.get().strip()
            price = float(self.product_price_entry.get())
            if price < 0:
                messagebox.showerror("Ошибка", "Цена не может быть отрицательной.")
                return
            product = Product(product_id, name, price)
            if self.db.add_product(product):
                messagebox.showinfo("Успех", "Товар добавлен.")
                self.load_products()
                self.clear_product_form()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить товар. Возможно, ID уже существует.")
        except ValueError:
            messagebox.showerror("Ошибка", "ID должен быть числом, цена - числом с точкой.")

    def load_products(self):
        """Отображает список товаров в таблице."""
        for row in self.product_tree.get_children():
            self.product_tree.delete(row)
        products = self.db.get_all_products()
        for p in products:
            self.product_tree.insert("", "end", values=(p.product_id, p.name, f"{p.price:.2f}"))

    def clear_product_form(self):
        self.product_id_entry.delete(0, tk.END)
        self.product_name_entry.delete(0, tk.END)
        self.product_price_entry.delete(0, tk.END)

    def delete_product(self):
        """Удаляет выбранный товар из базы данных и обновляет список."""
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для удаления.")
            return
        product_id = self.product_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Подтверждение", f"Удалить товар с ID {product_id}?"):
            if self.db.delete_product(product_id):
                messagebox.showinfo("Успех", "Товар удалён.")
                self.load_products()
                self.load_orders()  
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить товар.")

    
    def create_order_tab(self):
        """Создаёт вкладку для создания и просмотра заказов, включая сортировку и удаление."""
        frame = self.order_tab

        form_frame = ttk.LabelFrame(frame, text="Создать заказ")
        form_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(form_frame, text="ID заказа:").grid(row=0, column=0, sticky="e")
        self.order_id_entry = ttk.Entry(form_frame)
        self.order_id_entry.grid(row=0, column=1, sticky="w")

        ttk.Label(form_frame, text="ID клиента:").grid(row=1, column=0, sticky="e")
        self.order_client_id_entry = ttk.Entry(form_frame)
        self.order_client_id_entry.grid(row=1, column=1, sticky="w")

        ttk.Label(form_frame, text="ID товаров (через запятую):").grid(row=2, column=0, sticky="e")
        self.order_product_ids_entry = ttk.Entry(form_frame)
        self.order_product_ids_entry.grid(row=2, column=1, sticky="w")
        
        ttk.Label(form_frame, text="Дата заказа (ДД-ММ-ГГГГ или наоборот ):").grid(row=3, column=0, sticky="e")
        self.order_date_entry = ttk.Entry(form_frame)
        self.order_date_entry.grid(row=3, column=1, sticky="w")

        add_btn = ttk.Button(form_frame, text="Создать заказ", command=self.add_order)
        add_btn.grid(row=4, column=0, columnspan=2, pady=5)

        sort_frame = ttk.Frame(frame)
        sort_frame.pack(fill="x", padx=10)

        ttk.Label(sort_frame, text="Сортировать заказы по:").pack(side="left", padx=5)
        self.sort_var = tk.StringVar(value="date")
        sort_date_rb = ttk.Radiobutton(sort_frame, text="Дате", variable=self.sort_var, value="date", command=self.load_orders)
        sort_date_rb.pack(side="left")
        sort_total_rb = ttk.Radiobutton(sort_frame, text="Стоимость", variable=self.sort_var, value="total", command=self.load_orders)
        sort_total_rb.pack(side="left")

        list_frame = ttk.LabelFrame(frame, text="Список заказов")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID заказа", "Клиент", "Товары", "Дата", "Сумма")
        self.order_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.order_tree.heading(col, text=col)
            width = 150 if col != "Товары" else 300
            self.order_tree.column(col, width=width)
        self.order_tree.pack(fill="both", expand=True)

        refresh_btn = ttk.Button(list_frame, text="Обновить список", command=self.load_orders)
        refresh_btn.pack(pady=5)

        delete_btn = ttk.Button(frame, text="Удалить заказ", command=self.delete_order)
        delete_btn.pack(pady=5)

        self.load_orders()

    def add_order(self):
        """Обрабатывает создание нового заказа с проверкой корректности всех введённых данных. """
        try:
            order_id = int(self.order_id_entry.get())
            client_id = int(self.order_client_id_entry.get())
            product_ids_text = self.order_product_ids_entry.get().strip()
            date_text = self.order_date_entry.get().strip()

            client = self.db.get_client(client_id)
            if not client:
                messagebox.showerror("Ошибка", f"Клиент с ID {client_id} не найден.")
                return

            if not product_ids_text:
                messagebox.showerror("Ошибка", "Введите ID товаров через запятую.")
                return

            product_ids = [int(pid.strip()) for pid in product_ids_text.split(",") if pid.strip()]
            products: List[Product] = []
            for pid in product_ids:
                product = self.db.get_product(pid)
                if not product:
                    messagebox.showerror("Ошибка", f"Товар с ID {pid} не найден.")
                    return
                products.append(product)
                
            if not date_text:
                messagebox.showerror("Ошибка", "Введите дату заказа.")
                return
                
            date = None
            for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
                try:
                    date = datetime.strptime(date_text, fmt)
                    break
                except ValueError:
                    continue
            if date is None:
                messagebox.showerror("Ошибка", "Дата должна быть в формате ДД-ММ-ГГГГ или наоборот.")
                return

            order = Order(order_id, client, products, date)
            if self.db.add_order(order):
                messagebox.showinfo("Успех", "Заказ создан.")
                self.load_orders()
                self.clear_order_form()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать заказ. ID уже существует.")
        except ValueError:
            messagebox.showerror("Ошибка", "ID заказа, клиента и товаров должны быть числами.")

    def load_orders(self):
        """Загружает список заказов, сортирует и отображает в таблице."""
        for row in self.order_tree.get_children():
            self.order_tree.delete(row)
        sort_by = self.sort_var.get() if hasattr(self, "sort_var") else "date"
        orders = self.db.get_all_orders_sorted(sort_by=sort_by)
        for o in orders:
            products_names = ", ".join([p.name for p in o.products])
            order_date = o.date.strftime("%d-%m-%Y %H:%M:%S")
            total = f"{o.total_price():.2f}"
            self.order_tree.insert("", "end", values=(o.order_id, o.client.name, products_names, order_date, total))

    def clear_order_form(self):
        """Очищает поля формы создания заказа."""
        self.order_id_entry.delete(0, tk.END)
        self.order_client_id_entry.delete(0, tk.END)
        self.order_product_ids_entry.delete(0, tk.END)
        self.order_date_entry.delete(0, tk.END)  

    def delete_order(self):
        """Удаляет выбранный заказ из базы данных и обновляет список."""
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ для удаления.")
            return
        order_id = self.order_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Подтверждение", f"Удалить заказ с ID {order_id}?"):
            if self.db.delete_order(order_id):
                messagebox.showinfo("Успех", "Заказ удалён.")
                self.load_orders()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить заказ.")
                
    def create_analysis_tab(self):
        """Создаёт вкладку для аналитики с кнопками для различных визуализаций."""
        frame = self.analysis_tab

        label = ttk.Label(frame, text="Выберите визуализацию для отображения:", font=("Arial", 12))
        label.pack(pady=10)

        btn_top_clients = ttk.Button(frame, text="Топ 5 клиентов по числу заказов", command=self.show_top_clients)
        btn_top_clients.pack(fill="x", padx=20, pady=5)

        btn_orders_dynamics = ttk.Button(frame, text="Динамика количества заказов по датам", command=self.show_orders_dynamics)
        btn_orders_dynamics.pack(fill="x", padx=20, pady=5)

        btn_clients_graph = ttk.Button(frame, text="Граф связей клиентов по общим товарам", command=self.show_clients_graph)
        btn_clients_graph.pack(fill="x", padx=20, pady=5)


    def show_top_clients(self):
        """Отображает график топ 5 клиентов по числу заказов."""
        orders = self.db.get_all_orders()
        if not orders:
            messagebox.showinfo("Информация", "Нет данных для отображения.")
            return
        plot_top_clients_by_orders(orders, top_n=5)


    def show_orders_dynamics(self):
        """Отображает график динамики количества заказов по датам."""
        orders = self.db.get_all_orders()
        if not orders:
            messagebox.showinfo("Информация", "Нет данных для отображения.")
            return
        plot_orders_dynamics(orders)

    def show_clients_graph(self):
        """Строит и отображает граф связей клиентов по общим товарам."""
        orders = self.db.get_all_orders()
        clients = self.db.get_all_clients()
        if not orders or not clients:
            messagebox.showinfo("Информация", "Нет данных для отображения.")
            return
        G = build_clients_graph(orders)
        plot_clients_graph(G, clients)

if __name__ == "__main__":
    app = App()
    app.mainloop()

db.py
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

analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from typing import List
from models import Client, Product, Order
from datetime import datetime
from collections import Counter

sns.set(style="whitegrid")


def orders_to_dataframe(orders: List[Order]) -> pd.DataFrame:
    """Преобразует список заказов в DataFrame для анализа."""
    records = []
    for order in orders:
        for product in order.products:
            records.append({
                "order_id": order.order_id,
                "client_id": order.client.client_id,
                "client_name": order.client.name,
                "product_id": product.product_id,
                "product_name": product.name,
                "price": product.price,
                "date": order.date,
                "status": order.status
            })
    df = pd.DataFrame(records)
    return df


def plot_top_clients_by_orders(orders: List[Order], top_n: int = 5):
    """Строит столбчатую диаграмму топ N клиентов по количеству заказов."""
    df = orders_to_dataframe(orders)
    count_orders = df.groupby(["client_id", "client_name"])["order_id"].nunique().reset_index()
    count_orders = count_orders.sort_values(by="order_id", ascending=False).head(top_n)

    plt.figure(figsize=(10, 6))
    sns.barplot(x="order_id", y="client_name", data=count_orders, palette="viridis")
    plt.xlabel("Число заказов")
    plt.ylabel("Клиент")
    plt.title(f"Топ {top_n} клиентов по числу заказов")
    plt.tight_layout()
    plt.show()


def plot_orders_dynamics(orders: List[Order]):
    """Строит линейный график динамики количества заказов по датам."""
    df = orders_to_dataframe(orders)
    df['date_only'] = df['date'].dt.date
    orders_per_date = df.groupby('date_only')["order_id"].nunique().reset_index()

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=orders_per_date, x='date_only', y='order_id', marker='o')
    plt.xlabel("Дата")
    plt.ylabel("Количество заказов")
    plt.title("Динамика количества заказов по датам")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def build_clients_graph(orders: List[Order]):
    """Создаёт граф связей клиентов на основе общих товаров в заказах."""
    client_products = {}
    for order in orders:
        cid = order.client.client_id
        if cid not in client_products:
            client_products[cid] = set()
        for product in order.products:
            client_products[cid].add(product.product_id)

    """Создаем граф"""
    G = nx.Graph()

    """Добавляем узлы с метками клиентов (client_id)"""
    for cid in client_products:
        G.add_node(cid)

    """Добавляем ребра между клиентами, если у них есть общие товары"""
    clients = list(client_products.keys())
    for i in range(len(clients)):
        for j in range(i + 1, len(clients)):
            c1, c2 = clients[i], clients[j]
            common_products = client_products[c1].intersection(client_products[c2])
            if common_products:
                G.add_edge(c1, c2, weight=len(common_products))

    return G


def plot_clients_graph(G: nx.Graph, clients: List[Client]):
    """Строит визуализацию графа связей клиентов."""
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G, k=0.5, iterations=50)

    """Создаем словарь client_id -> name"""
    id_to_name = {c.client_id: c.name for c in clients}

    nx.draw_networkx_nodes(G, pos, node_size=500, node_color='skyblue')
    nx.draw_networkx_edges(G, pos, width=[G[u][v]['weight'] for u, v in G.edges()], alpha=0.7)
    nx.draw_networkx_labels(G, pos, labels=id_to_name, font_size=10)

    plt.title("Граф связей клиентов по общим товарам")
    plt.axis('off')
    plt.tight_layout()
    plt.show()