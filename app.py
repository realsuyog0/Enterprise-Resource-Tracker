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
        #     # Change "photo.png" to your file name if different
        #     st.image("photo.png", width=250) 
        # except:
        #     st.markdown("💎", unsafe_allow_html=True)
        st.markdown("<h1 style='color:white; margin-top:0;'>PS Jewelry</h1>", unsafe_allow_html=True)
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
st.set_page_config(page_title="PS Jewelry Manager", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0a2e1f !important; }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    .main { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("<h2 style='text-align: center; color: white;'>PS Jewelry</h2>", unsafe_allow_html=True)
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
            
            # Change 2: Handle "Sold Out" status visually
            if row['unit'] <= 0:
                r[4].markdown("<span style='color:red; font-weight:bold;'>Sold Out</span>", unsafe_allow_html=True)
            else:
                r[4].write(str(row['unit']))
                
            r[5].write(f"{row['cost_price']}"); r[6].write(f"{days_old}"); r[7].write(row['arrival_date'])

        if delete_ids:
            st.warning(f"You have selected {len(delete_ids)} item(s).")
            if st.button(f"🗑️ Delete Selected from {title}", type="primary"):
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
                        st.success(f"🔄 Restocked Sold Out item: {p_name}")
                    
                    #  If In Stock, only update if the price is the same
                    elif e_cost == p_cost:
                        new_total = e_unit + p_unit
                        conn.execute(
                            "UPDATE products SET unit = ?, arrival_date = ? WHERE id = ?",
                            (new_total, p_arrival.strftime("%Y-%m-%d"), e_id)
                        )
                        st.success(f"➕ Added units to existing stock.")
                    
                    #  If In Stock but price is different, create new row
                    else:
                        conn.execute(
                            "INSERT INTO products (product_name, code_number, unit, cost_price, arrival_date) VALUES (?,?,?,?,?)",
                            (p_name, p_code, p_unit, p_cost, p_arrival.strftime("%Y-%m-%d")))
                        st.success(f"✨ Different price detected. Created new row.")
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

    # 2. Layout for inputs 
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

    # Update session state with current inputs so data goes if page refreshes
    st.session_state.order_data.update({
        'c_name': c_name, 'c_phone': c_phone, 'c_addr': c_addr,
        'p_name': p_name, 'p_code': p_code, 'p_qty': p_qty
    })

    if st.button("Submit Order", type="primary"):
        if c_name and p_name:
            conn = sqlite3.connect(DB_NAME)
            
            #Collision check
            codes_in_stock = conn.execute(
                "SELECT DISTINCT code_number FROM products WHERE product_name = ? AND unit > 0", 
                (p_name,)
            ).fetchall()

            if len(codes_in_stock) > 1 and not p_code:
                st.error(f"⚠️ Multiple codes found for '{p_name}'. Please enter a valid code.")
                conn.close()
            else:
                # Search for specific stock
                if p_code:
                    stock = conn.execute("SELECT unit FROM products WHERE product_name = ? AND code_number = ?", (p_name, p_code)).fetchone()
                else:
                    stock = conn.execute("SELECT unit FROM products WHERE product_name = ?", (p_name,)).fetchone()

                if stock is None:
                    st.error(f"❌ Error: Product '{p_name}' not found. Check the name and try again.")
                    conn.close()
                elif stock[0] < p_qty:
                    st.error(f"❌ Error: Not enough stock!")
                    conn.close()
                else:
                    #  SUCCESS CASE 
                    conn.execute("INSERT INTO pending (customer_name, address, phone_number, product_name, product_number, quantity, payment_method, ordered_date) VALUES (?,?,?,?,?,?,?,?)",
                                 (c_name, c_addr, c_phone, p_name, p_code, p_qty, p_pay, p_date.strftime("%Y-%m-%d")))
                    conn.commit()
                    conn.close()
                    
                    # 3. DISPLAY BLUE MESSAGE IMMEDIATELY
                    msg_slot = st.empty()
                    msg_slot.info(f"✅ Success: Order for '{p_name}' placed on Pending list for {c_name}!")
                    
                    # 4. RESET DATA IN BACKGROUND
                    st.session_state.order_data = {
                        'c_name': '', 'c_phone': '', 'c_addr': '', 
                        'p_name': '', 'p_code': '', 'p_qty': 1
                    }

                    # 5. HOLD FOR 5 SECONDS
                    import time
                    time.sleep(5)
                    
                    # 6. CLEAR MESSAGE AND REFRESH FORM
                    msg_slot.empty()
                    st.rerun()
        else:
            st.error("Missing Info: Customer Name and Product Name are required.")

elif choice == "Pending":
    st.title("Pending Orders List")
    conn = sqlite3.connect(DB_NAME)
    df_p = pd.read_sql_query("SELECT * FROM pending", conn)
    conn.close()
    if not df_p.empty:
        select_all_p = st.checkbox("Select All Orders", key="psel_all")
        delete_ids_p = []
        h = st.columns([0.4, 0.4, 1.2, 1.5, 1.2, 0.8, 1.2, 1.2, 1.5])
        for i, cn in enumerate(["Del", "S.No", "Date", "Customer", "Product", "Qty", "Payment", "Phone", "Status"]): h[i].write(f"**{cn}**")
        for idx, (i, row) in enumerate(df_p.iterrows(), start=1):
            r = st.columns([0.4, 0.4, 1.2, 1.5, 1.2, 0.8, 1.2, 1.2, 1.5])
            is_checked_p = r[0].checkbox(" ", key=f"p_del_{row['id']}", value=select_all_p)
            if is_checked_p: delete_ids_p.append(row['id'])
            r[1].write(idx); r[2].write(row['ordered_date']); r[3].write(row['customer_name']); r[4].write(row['product_name'])
            r[5].write(str(row['quantity'])); r[6].write(row['payment_method']); r[7].write(row['phone_number'])
            with r[8]:
                s_price = st.number_input("Sell Price", min_value=0.0, key=f"sp_{row['id']}")
                if st.button("Confirm", key=f"sale_{row['id']}"):
                    conn = sqlite3.connect(DB_NAME)
                    item = conn.execute("SELECT cost_price FROM products WHERE product_name = ?", (row['product_name'],)).fetchone()
                    if item:
                        profit = (s_price - item[0]) * row['quantity']
                        conn.execute("UPDATE products SET unit = unit - ? WHERE product_name = ?", (row['quantity'], row['product_name']))
                        conn.execute("INSERT INTO sold (customer_name, phone_number, product_name, quantity, selling_price, profit, sold_date) VALUES (?,?,?,?,?,?,?)",
                                     (row['customer_name'], row['phone_number'], row['product_name'], row['quantity'], s_price, profit, row['ordered_date']))
                        conn.execute("DELETE FROM pending WHERE id = ?", (row['id'],))
                        conn.commit(); conn.close(); st.rerun()
                    else: st.error("Product Error!"); conn.close()

        if delete_ids_p:
            st.warning(f"{len(delete_ids_p)} orders selected.")
            if st.button("🗑️ Delete Selected Orders", type="primary"):
                conn = sqlite3.connect(DB_NAME)
                conn.execute(f"DELETE FROM pending WHERE id IN ({','.join(map(str, delete_ids_p))})")
                conn.commit(); conn.close(); st.rerun()
    else: st.info("No pending orders.")

elif choice == "Sold":
    st.title("Sales History")
    conn = sqlite3.connect(DB_NAME)
    df_s = pd.read_sql_query("SELECT * FROM sold", conn)
    conn.close()
    if not df_s.empty:
        h = st.columns([0.5, 1, 1.5, 1, 1.5, 0.8, 1.2, 1.2])
        for i, head in enumerate(["S.No", "Date", "Customer", "Number", "Product", "Unit", "Sell Price", "Profit"]): h[i].write(f"**{head}**")
        for idx, (i, row) in enumerate(df_s.iterrows(), start=1):
            r = st.columns([0.5, 1, 1.5, 1, 1.5, 0.8, 1.2, 1.2])
            r[0].write(idx); r[1].write(row['sold_date']); r[2].write(row['customer_name']); r[3].write(row['phone_number'])
            r[4].write(row['product_name']); r[5].write(str(row['quantity'])); r[6].write(f"{row['selling_price']}"); r[7].write(f"{row['profit']}")
    else: st.info("No sales yet.")

elif choice == "Analysis":
    st.markdown("<h3 style='text-align: center; color: #2d5a4c;'>Business Growth & Daily Wins ✨</h3>", unsafe_allow_html=True)
    conn = sqlite3.connect(DB_NAME)
    df_s = pd.read_sql_query("SELECT sold_date, profit, quantity FROM sold", conn)
    conn.close()
    if not df_s.empty:
        df_s['sold_date'] = pd.to_datetime(df_s['sold_date']).dt.date
        daily_stats = df_s.groupby('sold_date').agg(Total_Profit=('profit', 'sum'), Items_Sold=('quantity', 'sum')).reset_index()
        daily_stats = daily_stats.sort_values('sold_date')
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        total_items_lifetime = int(df_s['quantity'].sum())
        m1.metric("Lifetime Items Sold", f"{total_items_lifetime}")
        latest = daily_stats.iloc[-1]
        m2.metric("Today's Profit", f"Rs. {latest['Total_Profit']:,.0f} ✨")
        m3.metric("Today's Items", f"{int(latest['Items_Sold'])} Units")
        st.markdown("---")
        import plotly.express as px
        fig = px.bar(daily_stats, x='sold_date', y='Total_Profit', labels={'Total_Profit': 'Profit (Rs.)'}, hover_data=['Items_Sold'])
        fig.update_traces(marker_color='#2d5a4c', hoverlabel=dict(bgcolor="#164a33", font_color="white"))
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(type='category'), yaxis=dict(showgrid=False), height=350)
        st.plotly_chart(fig, use_container_width=True)
    else: st.info("Start confirming orders to see your analytics here!")

elif choice == "Settings":
    st.title("⚙️ System Settings")

    
    # --- 1. ACCESS KEY UPDATE ---
    with st.expander("🔐 Change Access Key", expanded=False):
        with st.form("change_key"):
            old_key = st.text_input("Current Key", type="password")
            new_key = st.text_input("New Key", type="password")
            if st.form_submit_button("Update Key"):
                conn = sqlite3.connect(DB_NAME)
                current = conn.execute("SELECT key_value FROM settings WHERE key_name = 'access_key'").fetchone()[0]
                if old_key == current:
                    conn.execute("UPDATE settings SET key_value = ? WHERE key_name = 'access_key'", (new_key,))
                    conn.commit()
                    conn.close()
                    st.success("✅ Key updated successfully!")
                else:
                    conn.close()
                    st.error("❌ Wrong current key.")

    st.divider()

        # --- 2. DATABASE BACKUP (DOWNLOAD) ---
    st.subheader("📥 Data Backup")
    st.write("Download a copy of your database to your computer.")
    try:
        with open(DB_NAME, "rb") as f:
            db_binary = f.read()
        
        st.download_button(
            label="Download .db Backup",
            data=db_binary,
            file_name=f"PSJ_Backup_{datetime.now().strftime('%Y_%m_%d')}.db",
            mime="application/octet-stream"
        )
    except Exception as e:
        st.error(f"Error preparing download: {e}")

    st.divider()

        # --- 3. DATABASE RESTORE (UPLOAD) ---
    st.subheader("📤 Restore System")
    st.warning("⚠️ Warning: Restoring will overwrite all current data with the uploaded file.")
    
    uploaded_file = st.file_uploader("Upload a previously downloaded .db file", type=["db"])
    
    if uploaded_file is not None:
        if st.button("🚀 Confirm Full Restore", type="primary"):
            try:
                # Close any active connections before overwriting
                import gc
                gc.collect() # Clears any hidden database connections
                
                with open(DB_NAME, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success("✅ Database restored! The app will now refresh.")
                import time
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Restore Failed: {e}. Ensure the file isn't open elsewhere.")
            