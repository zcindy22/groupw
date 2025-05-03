import streamlit as st
import requests

st.set_page_config(page_title="Admin", layout="centered")
st.title("Admin Dashboard")

if not st.session_state.get("logged_in"):
    st.warning("Please log in first from the Login page.")
    st.stop()

if st.session_state.get("role") != "admin":
    st.error("Access denied. Admins only.")
    st.stop()

# Admin content
st.success("Welcome, Admin!")

# Flask API URL
BASE_URL = 'http://localhost:5000/api'
POTENTIAL_URL = f'{BASE_URL}/potential'
BLACKLISTED_URL = f'{BASE_URL}/blacklisted'

st.title("Admin Panel – Blacklisted Words Manager")

# Section: Potential Words
st.header("Potential Blacklisted Words")

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

# Section: View Blacklisted Words
st.header("Confirmed Blacklisted Words")
response = requests.get(BLACKLISTED_URL)
if response.status_code == 200:
    st.write(response.json())
else:
    st.error("Failed to load blacklisted words.")
