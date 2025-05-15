import streamlit as st

st.set_page_config(page_title="Login", layout="centered")

from supabase_proj.db_utils import get_user_data, sign_in_user, check_reload
from argon2 import PasswordHasher

st.title("Login")

# Session state
for key, default in {
    "logged_in": False,
    "username": "",
    "role": "",
    "status": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


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

            #user_data = get_user_data(username)
            #if not user_data:
            #    st.error("User not found.")
            #    return

            #stored_hash = user_data[0].get("password_hash")
            #if not stored_hash:
               # st.error("No password found for this user.")
               # return

            try:
                sign_in_user(username, password)


            except Exception:
                st.error("Invalid password")

    sign_in()

else:

    st.write("You are logged in :)")
    if st.button("Log Out"):
        # Clear session state to log the user out
        st.session_state.clear()
        st.success("You have logged out successfully.")
        st.rerun()