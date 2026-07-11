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

    .stApp{
        background: linear-gradient(135deg,#0b1f3a 0%, #123b63 45%, #167c80 100%);
        color:#F8FAFC;
        font-family:"Segoe UI",sans-serif;
    }


    .login-box{
        background:rgba(255,255,255,0.08);
        backdrop-filter:blur(18px);

        border:1px solid rgba(255,255,255,0.15);

        border-radius:22px;

        padding:40px;

        max-width:470px;

        margin:auto;

        display:flex;
        flex-direction:column;
        align-items:center;

        box-shadow:
            0 15px 40px rgba(0,0,0,.35);
    }
                
    .stImage img{
        border-radius:18px;

        padding:10px;

        background:white;

        box-shadow:
            0 12px 30px rgba(0,0,0,.25);

        margin-bottom:25px;
    }

 
    .stButton>button{

        width:100%;

        border:none;

        border-radius:12px;

        padding:12px;

        font-size:16px;

        font-weight:600;

        color:white !important;

        background:linear-gradient(90deg,#0E5CAD,#1AAE9F);

        transition:.3s;

        box-shadow:
            0 8px 20px rgba(0,0,0,.25);

    }

    .stButton>button:hover{

        transform:translateY(-2px);

        background:linear-gradient(90deg,#0A4C90,#158D82);

    }


    div[data-baseweb="input"]{

        border-radius:12px;

        border:1px solid rgba(255,255,255,.15);

        background:rgba(255,255,255,.05);

    }

    div[data-baseweb="input"]:focus-within{

        border:1px solid #1AAE9F;

        box-shadow:0 0 0 3px rgba(26,174,159,.25);

    }

    input{
        color:white !important;
    }


    div[data-baseweb="select"]{

        border-radius:12px;

    }


    h1{
        color:white;
        font-weight:700;
        letter-spacing:.5px;
    }

    h2,h3,h4{
        color:#EAF4FF;
        font-weight:600;
    }

    p,label{
        color:#D6E4F0 !important;
    }

    hr{
        border:none;
        height:1px;
        background:rgba(255,255,255,.15);
    }


    ::-webkit-scrollbar{
        width:8px;
    }

    ::-webkit-scrollbar-thumb{
        background:#1AAE9F;
        border-radius:10px;
    }

    ::-webkit-scrollbar-track{
        background:#0b1f3a;
    }

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

    # --- 3. MAIN APP CONFIG ---
st.set_page_config(page_title="Resource Tracker", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0a2e1f !important; }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("<h2 style='text-align: center; color: white;'>Resource Tracker</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")
menu = ["InStock", "Unsold", "Orders", "Pending", "Sold", "Analysis", "Settings"]
choice = st.sidebar.radio(" ", menu)

st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    st.session_state["password_correct"] = False
    st.rerun()

    # --- SHARED UTILITY: DATA VIEW ---
def display_inventory_table(df, title):
    st.subheader(title)
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1: search_q = st.text_input(f"🔍 Search {title}", key=f"search_{title}")
    with col_s2: sort_by = st.selectbox("Sort", ["Newest", "Oldest", "Name"], key=f"sort_{title}")

    if not df.empty:
        if search_q:
            df = df[df.apply(lambda row: search_q.lower() in row.astype(str).str.lower().values, axis=1)]
        
        df = df.sort_values(by="arrival_date", ascending=(sort_by == "Oldest")) if "Date" in sort_by or "Newest" in sort_by or "Oldest" in sort_by else df.sort_values(by="product_name")

        select_all = st.checkbox("Select All Rows", key=f"all_{title}")
        delete_ids = []
        
        h = st.columns([0.5, 0.5, 2, 1.5, 1, 1, 1, 1.5])
        cols = ["Select", "S.No", "Product", "Code", "Unit", "Cost", "Days", "Arrival"]
        for i, col_name in enumerate(cols): h[i].write(f"**{col_name}**")

        today = datetime.now().date()
        for idx, (i, row) in enumerate(df.iterrows(), start=1):
            arrival_dt = datetime.strptime(row['arrival_date'], "%Y-%m-%d").date()
            days_old = (today - arrival_dt).days
            r = st.columns([0.5, 0.5, 2, 1.5, 1, 1, 1, 1.5])
            
            checked = r[0].checkbox(" ", key=f"del_{title}_{row['id']}", value=select_all)
            if checked:
                delete_ids.append(row['id'])
            
            r[1].write(idx)
            r[2].write(row['product_name']); r[3].write(row['code_number'])
            
            # Handle "Sold Out" status visually
            if row['unit'] <= 0:
                r[4].markdown("<span style='color:red; font-weight:bold;'>Sold Out</span>", unsafe_allow_html=True)
            else:
                r[4].write(str(row['unit']))
                
            r[5].write(f"{row['cost_price']}"); r[6].write(f"{days_old}"); r[7].write(row['arrival_date'])

        if delete_ids:
            st.warning(f"You have selected {len(delete_ids)} item(s).")
            if st.button(f" Delete Selected from {title}", type="primary"):
                conn = sqlite3.connect(DB_NAME)
                conn.execute(f"DELETE FROM products WHERE id IN ({','.join(map(str, delete_ids))})")
                conn.commit(); conn.close(); st.rerun()
    else: st.info(f"No items in {title}.")

# --- 4. MODULE LOGIC ---

conn = sqlite3.connect(DB_NAME)
full_df = pd.read_sql_query("SELECT * FROM products", conn)
conn.close()

if choice == "InStock":
    st.title("InStock Inventory")
    with st.expander("Add New Inventory Entry", expanded=True):
        with st.form("entry_form", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1: p_name, p_code = st.text_input("Product Name"), st.text_input("Code Number")
            with col2: p_cost, p_arrival = st.number_input("Cost Price", min_value=0.0), st.date_input("Arrival Date", datetime.now())
            with col3: p_unit = st.number_input("Unit", min_value=1, value=1)
            
            if st.form_submit_button("Submit"):
                conn = sqlite3.connect(DB_NAME)
                
                # Search for the item. Order by unit so that a '0' row is found first.
                existing = conn.execute(
                    "SELECT id, unit, cost_price FROM products WHERE product_name = ? AND code_number = ? ORDER BY unit ASC", 
                    (p_name, p_code)
                ).fetchone()

                if existing:
                    e_id, e_unit, e_cost = existing
                    
                    #  If the row is Out of Stock (0), ALWAYS update it (ignore price)
                    if e_unit <= 0:
                        conn.execute(
                            "UPDATE products SET unit = ?, cost_price = ?, arrival_date = ? WHERE id = ?",
                            (p_unit, p_cost, p_arrival.strftime("%Y-%m-%d"), e_id)
                        )
                        st.success(f" Restocked Sold Out item: {p_name}")
                    
                    #  If In Stock, only update if the price is the same
                    elif e_cost == p_cost:
                        new_total = e_unit + p_unit
                        conn.execute(
                            "UPDATE products SET unit = ?, arrival_date = ? WHERE id = ?",
                            (new_total, p_arrival.strftime("%Y-%m-%d"), e_id)
                        )
                        st.success(f" Added units to existing stock.")
                    
                    #  If In Stock but price is different, create new row
                    else:
                        conn.execute(
                            "INSERT INTO products (product_name, code_number, unit, cost_price, arrival_date) VALUES (?,?,?,?,?)",
                            (p_name, p_code, p_unit, p_cost, p_arrival.strftime("%Y-%m-%d")))
                        st.success(f" Different price detected. Created new row.")
                else:
                    # Brand new product
                    conn.execute(
                        "INSERT INTO products (product_name, code_number, unit, cost_price, arrival_date) VALUES (?,?,?,?,?)",
                        (p_name, p_code, p_unit, p_cost, p_arrival.strftime("%Y-%m-%d")))
                
                conn.commit()
                conn.close()
                st.rerun()
    if not full_df.empty:
        full_df['arrival_dt'] = pd.to_datetime(full_df['arrival_date']).dt.date
        full_df['days_diff'] = full_df['arrival_dt'].apply(lambda x: (datetime.now().date() - x).days)
        display_inventory_table(full_df[full_df['days_diff'] < 200], "Current InStock")

elif choice == "Unsold":
    st.title("Unsold Inventory")
    if not full_df.empty:
        full_df['arrival_dt'] = pd.to_datetime(full_df['arrival_date']).dt.date
        full_df['days_diff'] = full_df['arrival_dt'].apply(lambda x: (datetime.now().date() - x).days)
        display_inventory_table(full_df[full_df['days_diff'] >= 200], "Unsold Items")

    else: st.info("No pending orders.")

elif choice == "Orders":
    st.title("New Customer Order")

    # 1. Setup Session State to hold values when errors occur
    if 'order_data' not in st.session_state:
        st.session_state.order_data = {
            'c_name': '', 'c_phone': '', 'c_addr': '', 
            'p_name': '', 'p_code': '', 'p_qty': 1
        }

        #Input layouts remainsssss!!
        c1, c2 = st.columns(2)
    with c1:
        c_name = st.text_input("Customer Name", value=st.session_state.order_data['c_name'])
        c_phone = st.text_input("Phone Number", value=st.session_state.order_data['c_phone'])
        c_addr = st.text_area("Address", value=st.session_state.order_data['c_addr'])
    with c2: 
        p_name = st.text_input("Product Name", value=st.session_state.order_data['p_name'])
        p_code = st.text_input("Product Number (Code)", value=st.session_state.order_data['p_code'])
        p_qty = st.number_input("Quantity", min_value=1, value=st.session_state.order_data['p_qty'])
        p_pay = st.selectbox("Payment", ["Cash", "Fonepay", "D_Wallets"])
        p_date = st.date_input("Date", datetime.now())

    

            