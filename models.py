#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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

