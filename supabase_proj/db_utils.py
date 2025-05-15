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

def get_user_documents(user_id):
    client = SupabaseClient.get_client()
    response = client.table("texts").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return response.data if response.data else []

def get_shared_documents(user_id):
    client = SupabaseClient.get_client()

    # Get all text_ids from collaborations where user is the invitee and status is accepted
    collab_res = client.table("collaborations").select("text_id").eq("invitee_id", user_id).eq("status", "accepted").execute()
    text_ids = [row["text_id"] for row in collab_res.data]

    if not text_ids:
        return []

    # Get the actual text documents
    text_res = client.table("texts").select("*").in_("id", text_ids).execute()
    return text_res.data if text_res.data else []

def get_tokens(user_id):
    client = SupabaseClient.get_client()
    response = client.table("profiles").select("tokens").eq("id", user_id).single().execute()
    return response.data["tokens"] if response.data else 0

def update_tokens(user_id, change):
    client = SupabaseClient.get_client()

    # get current token amount
    user_data = client.table("profiles").select("tokens").eq("id", user_id).single().execute()
    current_tokens = user_data.data["tokens"]

    # add to token amount
    response = client.table("profiles").update({
        "tokens": current_tokens + change
    }).eq("id", user_id).execute()

    return response.data


def get_incoming_collab_requests(user_id):
    client = SupabaseClient.get_client()
    res = client.table("collaborations").select("*").eq("invitee_id", user_id).eq("status", "pending").execute()
    return res.data if res.data else []

def get_outgoing_collab_requests(user_id):
    client = SupabaseClient.get_client()
    res = client.table("collaborations").select("*").eq("inviter_id", user_id).eq("status", "pending").execute()
    return res.data if res.data else []


def respond_to_request(collab_id, action):  # action: "accepted" or "rejected"
    client = SupabaseClient.get_client()
    res = client.table("collaborations").update({"status": action}).eq("id", collab_id).execute()
    return res.data

def get_text_title(text_id):
    client = SupabaseClient.get_client()
    res = client.table("texts").select("docname").eq("id", text_id).single().execute()
    return res.data["docname"] if res.data else "(untitled)"

def get_user_data_by_email(email):
    client = SupabaseClient.get_client()
    res = client.table("profiles").select("*").eq("email", email).execute()
    return res.data if res.data else []

def send_collab_request(inviter_id, invitee_id, text_id):
    client = SupabaseClient.get_client()
    payload = {
        "inviter_id": inviter_id,
        "invitee_id": invitee_id,
        "text_id": text_id,
        "status": "pending"
    }
    client.table("collaborations").insert(payload).execute()

def submit_complaint_by_email(complainer_id, accused_email, text_id, reason):
    client = SupabaseClient.get_client()

    # Look up accused user's ID from their email
    accused_res = client.table("profiles").select("id").eq("email", accused_email).single().execute()
    if not accused_res.data:
        raise Exception("User with that email not found.")
    
    accused_id = accused_res.data["id"]

    # Insert complaint
    payload = {
        "complainer_id": complainer_id,
        "accused_id": accused_id,
        "text_id": text_id,
        "reason": reason,
        "status": "pending",
        "decision": None,
        "reviewed_by": None
    }
    res = client.table("complaints").insert(payload).execute()
    return res.data
