import streamlit as st
import requests
import json
import os

# ---------- Page Config ----------
st.set_page_config(page_title="Admin", layout="centered")
st.title("Admin Dashboard")

# ---------- Restore login if session lost ----------
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

# ---------- File Utilities ----------
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
try:
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
                        st.rerun()
                with col3:
                    if st.button("❌ Deny", key=f"deny-{word}"):
                        res = requests.post(f"{POTENTIAL_URL}/deny/{word}")
                        st.warning(res.json().get("message", "Denied"))
                        st.rerun()
    else:
        st.error("Failed to fetch potential words.")
except requests.exceptions.ConnectionError:
    st.error("⚠️ Could not connect to the blacklisted words API.")

# ---------- Confirmed List ----------
st.subheader("🚫 Confirmed Blacklisted Words")
try:
    response = requests.get(BLACKLISTED_URL)
    if response.status_code == 200:
        st.write(response.json())
    else:
        st.error("Failed to load blacklisted words.")
except requests.exceptions.ConnectionError:
    st.error("⚠️ Could not connect to the blacklisted words API.")

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

            st.markdown("**Choose an action:**")
            action = st.selectbox(
                f"Action for Complaint #{i+1}",
                options=["No Action", "Penalize Complainer", "Penalize Reported User"],
                key=f"action_{i}"
            )
            penalty_amt = st.number_input(
                "Token Penalty Amount (if applicable)", min_value=0, max_value=50, value=0, key=f"penalty_amt_{i}"
            )

            if st.button("✅ Apply Action", key=f"apply_{i}"):
                if action == "Penalize Complainer" and penalty_amt > 0:
                    update_tokens(c['from'], -penalty_amt)
                    notifications.append({
                        "to": c['from'],
                        "message": f"You were penalized {penalty_amt} tokens for a rejected complaint."
                    })
                    st.success(f"{penalty_amt} tokens deducted from complainer.")

                elif action == "Penalize Reported User" and penalty_amt > 0:
                    update_tokens(c['about'], -penalty_amt)
                    notifications.append({
                        "to": c['about'],
                        "message": f"You were penalized {penalty_amt} tokens due to a confirmed complaint."
                    })
                    st.success(f"{penalty_amt} tokens deducted from reported user.")

                elif action == "No Action":
                    st.info("No penalty applied.")

                else:
                    st.warning("Penalty must be greater than 0 to apply.")

                complaints.pop(i)
                save_complaints(complaints)
                save_notifications(notifications)
                st.rerun()
else:
    st.info("No complaints submitted yet.") 
