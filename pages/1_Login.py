import streamlit as st
from supabase_proj.db_utils import get_user_data
from argon2 import PasswordHasher

st.set_page_config(page_title="Login", layout="centered")
st.title("Login")

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'username' not in st.session_state:
    st.session_state.username = ""

if 'role' not in st.session_state:
    st.session_state.role = ""

# Set up the password hasher
ph = PasswordHasher()

if not st.session_state.logged_in:
    def sign_in():
        st.write("Please enter your credentials to access your account.")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In")

        if submit:
            if not username or not password:
                st.warning("Please fill out both fields.")
                return

            user_data = get_user_data(username)
            if not user_data:
                st.error("User not found.")
                return

            stored_hash = user_data[0].get("password_hash")
            if not stored_hash:
                st.error("No password found for this user.")
                return

            try:
                ph.verify(stored_hash, password)
                st.success(f"Welcome back, {username}!")

                # Set session state
                st.session_state.logged_in = True
                st.session_state.username = username

            except Exception as e:
                st.error("Invalid password")

    if __name__ == "__main__":
        sign_in()

else: 
    st.write("You are logged in :)")
    if st.button("Log Out"):
        # Clear session state to log the user out
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.success("You have logged out successfully.")
        st.rerun()