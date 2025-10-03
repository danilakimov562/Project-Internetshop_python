#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

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


