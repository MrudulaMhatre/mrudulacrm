import json
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import pandas as pd
import plotly.express as px

# Firebase Initialization
if not firebase_admin._apps:
    cred = credentials.Certificate("crmmanagement-e3aa6-firebase-adminsdk-fbsvc-d46a9ce133.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -------------------- AUTHENTICATION SYSTEM --------------------
def register_user(email, password, name):
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({"email": email, "name": name, "role": "user"})
        return True, "Registration successful!"
    except Exception as e:
        return False, str(e)

def login_user(email, password):
    try:
        user = auth.get_user_by_email(email)
        return True, user.uid
    except Exception as e:
        return False, str(e)

# -------------------- UI COMPONENTS --------------------
st.set_page_config(page_title="CRM System", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None

def login_page():
    st.title("🔐 CRM Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        success, response = login_user(email, password)
        if success:
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = response
            st.rerun()
        else:
            st.error(response)
    
    st.subheader("New User?")
    name = st.text_input("Full Name")
    reg_email = st.text_input("Register Email")
    reg_password = st.text_input("Register Password", type="password")

    if st.button("Register"):
        success, message = register_user(reg_email, reg_password, name)
        if success:
            st.success(message)
        else:
            st.error(message)

# -------------------- DASHBOARD --------------------
def dashboard():
    st.sidebar.title("📊 CRM Dashboard")
    menu = ["Dashboard", "Customers", "Leads", "Tasks", "Logout"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Dashboard":
        st.title("📊 Overview")
        customers = db.collection("customers").stream()
        leads = db.collection("leads").stream()
        tasks = db.collection("tasks").stream()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Customers", sum(1 for _ in customers))
        col2.metric("Total Leads", sum(1 for _ in leads))
        col3.metric("Total Tasks", sum(1 for _ in tasks))
    
    elif choice == "Customers":
        manage_customers()

    elif choice == "Leads":
        manage_leads()

    elif choice == "Tasks":
        manage_tasks()

    elif choice == "Logout":
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.rerun()

# -------------------- CUSTOMER MANAGEMENT --------------------
def manage_customers():
    st.title("👥 Manage Customers")
    name = st.text_input("Customer Name")
    email = st.text_input("Customer Email")
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")

    if st.button("Add Customer"):
        db.collection("customers").add({"name": name, "email": email, "phone": phone, "address": address})
        st.rerun()

    customers = db.collection("customers").stream()
    data = [{"ID": c.id, **c.to_dict()} for c in customers]
    if data:
        st.dataframe(pd.DataFrame(data))

# -------------------- LEAD MANAGEMENT --------------------
def manage_leads():
    st.title("📞 Manage Leads")
    lead_name = st.text_input("Lead Name")
    contact = st.text_input("Contact Info")
    status = st.selectbox("Status", ["New", "In Progress", "Converted", "Lost"])

    if st.button("Add Lead"):
        db.collection("leads").add({"name": lead_name, "contact": contact, "status": status})
        st.rerun()

    leads = db.collection("leads").stream()
    data = [{"ID": l.id, **l.to_dict()} for l in leads]
    if data:
        st.dataframe(pd.DataFrame(data))

# -------------------- TASK MANAGEMENT --------------------
def manage_tasks():
    st.title("✅ Assign Tasks")
    task_name = st.text_input("Task Name")
    assignee = st.text_input("Assignee Name")
    deadline = st.date_input("Deadline")

    if st.button("Assign Task"):
        db.collection("tasks").add({"task": task_name, "assignee": assignee, "deadline": str(deadline)})
        st.rerun()

    tasks = db.collection("tasks").stream()
    data = [{"ID": t.id, **t.to_dict()} for t in tasks]
    if data:
        st.dataframe(pd.DataFrame(data))

# -------------------- MAIN --------------------
if st.session_state["logged_in"]:
    dashboard()
else:
    login_page()
