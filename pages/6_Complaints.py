import streamlit as st
import json
import os

COMPLAINTS_FILE = "complaints.json"

# ---------- Helpers ----------
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def load_complaints():
    return load_json(COMPLAINTS_FILE, [])

def save_complaints(complaints):
    save_json(COMPLAINTS_FILE, complaints)

# ---------- Auth ----------
user = st.session_state.get("username")
role = st.session_state.get("role", "")

# Restore login state from cache file (if session lost on refresh)
if not st.session_state.get("logged_in") and os.path.exists("auth_cache.json"):
    with open("auth_cache.json", "r") as f:
        data = json.load(f)
        st.session_state.logged_in = data.get("logged_in", False)
        st.session_state.username = data.get("username", "")
        st.session_state.role = data.get("role", "")

if not user:
    st.error("Please log in to access this page.")
    st.stop()

st.set_page_config(page_title="Complaints", layout="centered")
st.title("📣 File a Complaint")

# ---------- Complaint Form ----------
st.subheader("Submit a Complaint")
with st.form("complaint_form"):
    complaint_user = st.text_input("Who are you reporting?")
    complaint_reason = st.text_area("Why are you reporting them?")
    submit_complaint = st.form_submit_button("Submit Complaint")

if submit_complaint:
    if not complaint_user or not complaint_reason:
        st.warning("Please fill out all fields.")
    else:
        complaints = load_complaints()
        complaints.append({
            "from": user,
            "about": complaint_user,
            "reason": complaint_reason
        })
        save_complaints(complaints)
        st.success("Complaint submitted. A super-user will review it.")