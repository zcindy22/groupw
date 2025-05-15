# supabase/db_utils.py
import supabase
from supabase_proj.client import SupabaseClient
import streamlit as st

@st.cache_data
def get_user_data(id: str):
    client = SupabaseClient.get_client()
    response = client.table("profiles").select("*").eq("id", id).execute()
    return response.data  # This is a list of matching user records

def insert_user(username: str, password_hash: str):
    client = SupabaseClient.get_client()
    response = client.table("users").insert({
        "username": username,
        "password_hash": password_hash
    }).execute()
    return response.data

def suspend_user():
    client = SupabaseClient.get_service_client()
    client.table("profiles").update({
    "status": "suspended"}).eq("id", st.session_state.id).execute()

def add_tokens(amount: int):
    client = SupabaseClient.get_client()

    # get current token amount
    user_data = client.table("profiles").select("tokens").eq("id", st.session_state.id).single().execute()
    current_tokens = user_data.data["tokens"]

    # add to token amount
    response = client.table("profiles").update({
        "tokens": current_tokens + amount
    }).eq("id", st.session_state.id).execute()

    return response.data

def sign_up(email, password):
    try:
        client = SupabaseClient.get_client()

        # Supabase Auth sign-up
        result = client.auth.sign_up({"email": email, "password": password})

        # Check if the sign-up was successful
        user = result.user
        if user is None:
            raise Exception("Sign-up failed: user not created")

        user_id = user.id  # UUID from Supabase Auth
        
        st.session_state.logged_in = True
        st.session_state.email = email
        st.session_state.id = user_id
        user_data = get_user_data(user_id)
        st.session_state.role = user_data[0].get("role")
        st.session_state.status = user_data[0].get("status")

    except Exception as e:
        raise Exception(f"Error during sign-up: {e}")

def sign_in_user(email, password):
    try:
        client = SupabaseClient.get_client()
        response = client.auth.sign_in_with_password({"email": email, "password": password})
        
        if response:
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.id = response.user.id
            user_data = get_user_data(st.session_state.id)
            st.session_state.role = user_data[0].get("role")
            st.session_state.status = user_data[0].get("status")
            
            st.success(f"Welcome back, {email}!")
        else:
            st.error("Invalid email or password.")
    except Exception as e:
        st.error(f"Error logging in: {e}")


def get_blacklist():
    client = SupabaseClient.get_client()
    response = client.table("blacklist").select("word").eq("status", "approved").execute()
    return {row["word"].lower() for row in response.data} if response.data else set()


# Add this function to allow users to submit blacklist suggestions
def suggest_blacklist_word(word: str):
    client = SupabaseClient.get_client()
    payload = {"word": word, "status": "pending"}
    payload["submitted_by"] = st.session_state.id  # must match uuid if used
    response = client.table("blacklist").insert(payload).execute()
    return response.data

def add_reload():
    client = SupabaseClient.get_client()

    if "user" not in st.session_state:
        session_rows = client.table("sessions").select("*").order("created_at", desc=True).limit(1).execute()

        if session_rows.data:
            token = session_rows.data[0]["refresh_token"]
            restored = client.auth.set_session(access_token=None, refresh_token=token)

            if restored.session:
                st.session_state.user = restored.user
                st.session_state.email = restored.user.email
                st.session_state.user_id = restored.user.id
                st.session_state.refresh_token = restored.session.refresh_token
                st.session_state.logged_in = True


def check_reload():
    client = SupabaseClient.get_client()
    session_res = client.table("sessions").select("*").order("created_at", desc=True).limit(1).execute()
    
    if session_res.data:
        refresh_token = session_res.data[0]["refresh_token"]
        restored = client.auth.set_session(access_token=None, refresh_token=refresh_token)
        
        if restored.session:
            st.session_state.user = restored.user
            st.session_state.email = restored.user.email
            st.session_state.id = restored.user.id
            st.session_state.refresh_token = restored.session.refresh_token
            st.session_state.logged_in = True