import streamlit as st
from argon2 import PasswordHasher
from supabase_proj.db_utils import insert_user
from supabase_proj.db_utils import get_user_data

ph = PasswordHasher()

st.set_page_config(page_title="Sign Up", layout="centered")
st.title("Sign Up")

# Form to register new users
with st.form("signup_form"):
    st.subheader("Create your account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    #type password lets user hide the field
    confirm_password = st.text_input("Confirm Password", type="password")
    submit = st.form_submit_button("Sign Up")

    if submit:
        if not username or not password or not confirm_password:
            st.error("Please fill in all the fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            # Replace this with actual user registration logic (e.g. save to DB)
            exist_user = get_user_data(username)
            if exist_user:
                st.error("Username taken")
            
            pass_hash = ph.hash(password)

            try: 
                insert_user(username, pass_hash)
                st.success("Account Created! Welcome!")
                st.rerun()

            except Exception as e: 
                st.error(f"Error: {e}")
