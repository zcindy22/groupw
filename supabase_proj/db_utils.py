# supabase/db_utils.py
import supabase
from supabase_proj.client import SupabaseClient
import streamlit as st

@st.cache_data
def get_user_data(id: str):
    client = SupabaseClient.get_client()
    response = client.table("profiles").select("*").eq("id", id).execute()
    return response.data  # This is a list of matching user records

def see_username_exist(email: str):
    client = SupabaseClient.get_client()
    response = client.table("profiles").select("*").eq("email", email).execute()
    return response.data  # This is a list of matching user records

def suspend_user():
    client = SupabaseClient.get_service_client()
    client.table("profiles").update({
    "status": "suspended"}).eq("id", st.session_state.id).execute()
    st.session_state.status = "suspended"

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
        try:
            user_data = get_user_data(user_id)
            st.session_state.role = user_data[0].get("role")
            st.session_state.status = user_data[0].get("status")
        except Exception as inner:
            raise Exception(f"Sign-up worked, but fetching profile failed: {inner}")

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

def get_collaborations():
    client = SupabaseClient.get_client()
    response = client.rpc("get_user_collaborations", {"_user_id": st.session_state.id}).execute()
    st.session_state.collab_requests = response.data

def accept_collaboration():

    client = SupabaseClient.get_service_client()
    client.table("collaborations") \
        .update({"status": "accepted"}) \
        .eq("id", st.session_state.accepted_collaboration_id) \
        .execute()

def reject_collaboration():
    client = SupabaseClient.get_service_client()
    response = client.table("collaborations") \
        .update({"status": "rejected"}) \
        .eq("id", st.session_state.accepted_collaboration_id) \
        .execute()
    
    text_id = response.data[0]["text_id"]

    client.table("texts") \
        .update({"status": "single"}) \
        .eq("id", text_id) \
        .execute()

def show_complains():
    client = SupabaseClient.get_client()
    response = client.table("complaints").select("*") \
        .eq("complainer_id", st.session_state.id).eq("seen", "show").neq("status", "pending").execute()
    st.session_state.complaint_updates = response.data

def dismiss_complains(complaint_id):
    client = SupabaseClient.get_service_client()
    client.table("complaints") \
        .update({"seen": "hide"}) \
        .eq("id", complaint_id) \
        .execute()

def show_against_complains():
    client = SupabaseClient.get_client()
    response = client.table("complaints").select("*") \
        .eq("accused_id", st.session_state.id).eq("seen", "show").neq("status", "pending").execute()
    st.session_state.complaints_against_user = response.data

def dismiss_against_complains(accused_id):
    client = SupabaseClient.get_service_client()
    client.table("complaints") \
        .update({"seen": "hide"}) \
        .eq("id", accused_id) \
        .execute()

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
