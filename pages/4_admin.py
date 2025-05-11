import streamlit as st
import requests
import json
import os

# ---------- Page Config ----------
st.set_page_config(page_title="Admin", layout="centered")
st.title("Admin Dashboard")

# Restore login state from cache file (if session lost on refresh)
if not st.session_state.get("logged_in") and os.path.exists("auth_cache.json"):
    with open("auth_cache.json", "r") as f:
        data = json.load(f)
        st.session_state.logged_in = data.get("logged_in", False)
        st.session_state.username = data.get("username", "")
        st.session_state.role = data.get("role", "")

if not st.session_state.get("logged_in"):
    st.warning("Please log in first from the Login page.")
    st.stop()

user = st.session_state.get("username")
role = st.session_state.get("role", "")

if user == "iramraeesah":
    st.session_state["is_admin"] = True

if role != "admin" and not st.session_state.get("is_admin"):
    st.error("Access denied. Admins only.")
    st.stop()

# ---------- Local File Utilities ----------
COMPLAINTS_FILE = "complaints.json"
TOKEN_FILE = "tokens.json"
NOTIFICATIONS_FILE = "notifications.json"

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

def save_complaints(data):
    save_json(COMPLAINTS_FILE, data)

def load_notifications():
    return load_json(NOTIFICATIONS_FILE, [])

def save_notifications(data):
    save_json(NOTIFICATIONS_FILE, data)

def update_tokens(username, change):
    tokens = load_json(TOKEN_FILE, {})
    tokens[username] = max(0, tokens.get(username, 50) + change)
    save_json(TOKEN_FILE, tokens)

# ---------- Blacklisted Word Moderation ----------
st.header("⚙️ Blacklisted Words Manager")
BASE_URL = 'http://localhost:5000/api'
POTENTIAL_URL = f'{BASE_URL}/potential'
BLACKLISTED_URL = f'{BASE_URL}/blacklisted'

st.subheader("🕵️ Review Potential Words")
response = requests.get(POTENTIAL_URL)
if response.status_code == 200:
    potential_words = response.json()
    if not potential_words:
        st.info("No potential blacklisted words at the moment.")
    else:
        for word in potential_words:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{word}**")
            with col2:
                if st.button("✅ Approve", key=f"approve-{word}"):
                    res = requests.post(f"{POTENTIAL_URL}/approve/{word}")
                    st.success(res.json().get("message", "Approved"))
                    st.experimental_rerun()
            with col3:
                if st.button("❌ Deny", key=f"deny-{word}"):
                    res = requests.post(f"{POTENTIAL_URL}/deny/{word}")
                    st.warning(res.json().get("message", "Denied"))
                    st.experimental_rerun()
else:
    st.error("Failed to fetch potential words.")

# ---------- Confirmed List ----------
st.subheader("🚫 Confirmed Blacklisted Words")
response = requests.get(BLACKLISTED_URL)
if response.status_code == 200:
    st.write(response.json())
else:
    st.error("Failed to load blacklisted words.")

# ---------- Complaint Review ----------
st.markdown("---")
st.subheader("📨 Review Submitted Complaints")

complaints = load_complaints()
notifications = load_notifications()

if complaints:
    for i, c in enumerate(complaints):
        with st.expander(f"Complaint #{i+1} from `{c['from']}` about `{c['about']}`"):
            st.write(f"**Reason:** {c['reason']}")
            if c.get("rebuttal"):
                st.info(f"**Rebuttal:** {c['rebuttal']}")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🗑️ Delete Complaint", key=f"del_{i}"):
                    complaints.pop(i)
                    save_complaints(complaints)
                    st.success("Complaint deleted.")
                    st.experimental_rerun()

            with col2:
                penalty_from = st.number_input(f"Penalty to complainer", min_value=1, max_value=50, value=5, key=f"penalty_from_{i}")
                if st.button("⚠️ Penalize Complainer", key=f"penalize_from_{i}"):
                    update_tokens(c['from'], -penalty_from)
                    notifications.append({"to": c['from'], "message": f"You were penalized {penalty_from} tokens for an invalid complaint."})
                    save_notifications(notifications)
                    st.success(f"{penalty_from} tokens deducted from complainer.")

            with col3:
                penalty_about = st.number_input(f"Penalty to reported user", min_value=1, max_value=50, value=5, key=f"penalty_about_{i}")
                if st.button("⚠️ Penalize Reported User", key=f"penalize_about_{i}"):
                    update_tokens(c['about'], -penalty_about)
                    notifications.append({"to": c['about'], "message": f"You were penalized {penalty_about} tokens due to a confirmed complaint."})
                    save_notifications(notifications)
                    st.success(f"{penalty_about} tokens deducted from reported user.")
else:
    st.info("No complaints submitted yet.")
