import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# Initialize SQLite connection
conn = sqlite3.connect('transactions.db')
c = conn.cursor()

# Create a table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                type TEXT,
                amount REAL,
                balance REAL,
                location TEXT,
                company_name TEXT
            )''')
conn.commit()

# Initialize the balance (fetch the latest balance from the database)
def get_latest_balance():
    c.execute("SELECT balance FROM transactions ORDER BY id DESC LIMIT 1")
    result = c.fetchone()
    return result[0] if result else 0.0

st.session_state['balance'] = get_latest_balance()

# Title of the app
st.title("Daily Account Balance Tracker")

# Current balance display
st.header(f"Current Balance: LKR{st.session_state['balance']:.2f}")

# Buttons to switch between Cash Deposit and Pass Cheque
col1, col2 = st.columns(2)

with col1:
    if st.button("Cash Deposit"):
        st.session_state['transaction_type'] = "Cash Deposit"

with col2:
    if st.button("Pass Cheque"):
        st.session_state['transaction_type'] = "Pass Cheque"

# Conditionally display forms based on selected transaction type
if st.session_state.get('transaction_type') == "Cash Deposit":
    st.subheader("Cash Deposit")
    with st.form(key="cash_deposit_form"):
        # Date input
        date = st.date_input("Transaction Date", datetime.now().date())
        
        # Deposit location
        location = st.selectbox("Deposit Location", ("Gampaha", "Nittambuwa"))

        # Amount input
        amount = st.number_input("Deposit Amount", min_value=0.0, format="%.2f")

        # Submit button for Cash Deposit
        submit = st.form_submit_button(label="Submit Cash Deposit")

        if submit:
            st.session_state['balance'] += amount
            transaction_entry = {
                "date": date.strftime("%Y-%m-%d"),
                "type": f"Deposit ({location})",
                "amount": amount,
                "balance": st.session_state['balance'],
                "location": location,
                "company_name": None
            }
            
            # Insert transaction into the SQLite database
            c.execute('''INSERT INTO transactions (date, type, amount, balance, location, company_name) 
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (transaction_entry['date'], transaction_entry['type'], transaction_entry['amount'],
                       transaction_entry['balance'], transaction_entry['location'], transaction_entry['company_name']))
            conn.commit()
            
            st.success(f"Cash Deposit of ${amount:.2f} at {location} added.")
            st.experimental_rerun()

elif st.session_state.get('transaction_type') == "Pass Cheque":
    st.subheader("Pass Cheque")
    with st.form(key="pass_cheque_form"):
        # Date input
        date = st.date_input("Transaction Date", datetime.now().date())

        # Company name input
        company_name = st.text_input("Company Name on Cheque", "")

        # Amount input
        amount = st.number_input("Cheque Amount", min_value=0.0, format="%.2f")

        # Submit button for Pass Cheque
        submit = st.form_submit_button(label="Submit Cheque")

        if submit:
            st.session_state['balance'] -= amount
            transaction_entry = {
                "date": date.strftime("%Y-%m-%d"),
                "type": f"Cheque Passed (Company: {company_name})",
                "amount": -amount,
                "balance": st.session_state['balance'],
                "location": None,
                "company_name": company_name
            }
            
            # Insert transaction into the SQLite database
            c.execute('''INSERT INTO transactions (date, type, amount, balance, location, company_name) 
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (transaction_entry['date'], transaction_entry['type'], transaction_entry['amount'],
                       transaction_entry['balance'], transaction_entry['location'], transaction_entry['company_name']))
            conn.commit()
            
            st.success(f"Cheque of ${amount:.2f} from {company_name} added.")
            st.experimental_rerun()

# Display the transaction history from the database
st.subheader("Transaction History")
df = pd.read_sql_query("SELECT date, type, amount, balance FROM transactions", conn)
st.dataframe(df)
