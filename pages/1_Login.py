import streamlit as st
from supabase_proj.db_utils import get_user_data
from argon2 import PasswordHasher
import json
import os

st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Login")

# ------------- Session Defaults -------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ""

if 'role' not in st.session_state:
    st.session_state.role = ""

# ------------- Password Hasher -------------
ph = PasswordHasher()

# ------------- Login Form -------------
if not st.session_state.logged_in:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In")

    if submit:
        if not username or not password:
            st.warning("Please enter both fields.")
        else:
            user_data = get_user_data(username)
            if not user_data:
                st.error("User not found.")
            else:
                stored_hash = user_data[0].get("password_hash")
                if stored_hash:
                    try:
                        ph.verify(stored_hash, password)
                        # ✅ Set session values
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.role = user_data[0].get("role", "")

                        # ✅ Save to auth cache (for refresh persistence)
                        with open("auth_cache.json", "w") as f:
                            json.dump({
                                "logged_in": True,
                                "username": username,
                                "role": st.session_state.role
                            }, f)

                        st.success(f"Welcome back, {username}!")
                        st.rerun()  # Reload the page without showing old state
                    except Exception:
                        st.error("Invalid password.")
                else:
                    st.error("Password not set for this user.")
else:
    st.success(f"✅ Logged in as `{st.session_state.username}`")
    if st.button("Log Out"):
        # Clear session + auth cache
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""

        if os.path.exists("auth_cache.json"):
            os.remove("auth_cache.json")

        st.success("You have been logged out.")
        st.rerun()