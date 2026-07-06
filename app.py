import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# DATABASE INITIALIZATION
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'project_filebrowser.db')

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Fresh table for products
    conn.execute('''CREATE TABLE IF NOT EXISTS products 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    product_name TEXT, 
                    code_number TEXT, 
                    unit INTEGER, 
                    cost_price REAL, 
                    sp REAL DEFAULT 0.0, 
                    arrival_date TEXT)''')
    
    # Fresh table for pending orders
    conn.execute('''CREATE TABLE IF NOT EXISTS pending 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    customer_name TEXT, 
                    address TEXT, 
                    phone_number TEXT, 
                    product_name TEXT, 
                    product_number TEXT, 
                    quantity INTEGER, 
                    payment_method TEXT, 
                    ordered_date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sold 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  customer_name TEXT, phone_number TEXT, product_name TEXT, 
                  quantity INTEGER, selling_price REAL, profit REAL, sold_date TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS settings (key_name TEXT, key_value TEXT)''')
    check = c.execute("SELECT * FROM settings WHERE key_name = 'access_key'").fetchone()
    if not check:
        c.execute("INSERT INTO settings VALUES ('access_key', 'admin123')")
        
    conn.commit()
    conn.close()

init_db()
