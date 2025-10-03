#!/usr/bin/env python
# coding: utf-8

# In[ ]:


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



