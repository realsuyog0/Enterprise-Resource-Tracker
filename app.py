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


#  LOGIN PAGE SETUP
def login_page():
    st.markdown("""
        <style>
        .stApp { background: linear-gradient(135deg, #0a2e1f 0%, #164a33 50%, #2d5a4c 100%); color: white; }
        .login-box { 
            background-color: rgba(255, 255, 255, 0.05); 
            padding: 30px; 
            border-radius: 20px; 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            backdrop-filter: blur(15px); 
            text-align: center; 
            max-width: 450px; 
            margin: auto; 
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .stImage > img {
            border-radius: 15px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0px 8px 20px rgba(0,0,0,0.4);
            margin-bottom: 20px;
        }
        .stButton>button { background: #2d5a4c !important; color: white !important; width: 100%; border-radius: 10px; }
        </style>
        """, unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        # try:
        
        #     st.image("photo.png", width=250) 
        # except:
        #     st.markdown(" ", unsafe_allow_html=True)
        st.markdown("<h1 style='color:white; margin-top:0;'>Enterprise-Resource-Tracker</h1>", unsafe_allow_html=True)
        access_key_input = st.text_input("Access Key", type="password")
        if st.button("Unlock System"):
            conn = sqlite3.connect(DB_NAME)
            correct_key = conn.execute("SELECT key_value FROM settings WHERE key_name = 'access_key'").fetchone()[0]
            conn.close()
            if access_key_input == correct_key:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Invalid Access Key")
        st.markdown("</div>", unsafe_allow_html=True)

if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
    login_page()
    st.stop()