# supabase/db_utils.py
from supabase_proj.client import SupabaseClient
from supabase_proj.client import SupabaseClient

def get_user_data(username: str):
    client = SupabaseClient.get_client()
    response = client.table("users").select("*").eq("username", username).execute()
    return response.data  # This is a list of matching user records

def insert_user(username: str, password_hash: str):
    client = SupabaseClient.get_client()
    response = client.table("users").insert({
        "username": username,
        "password_hash": password_hash
    }).execute()
    return response.data


def get_blacklist():
    client = SupabaseClient.get_client()
    response = client.table("blacklist").select("word").eq("status", "approved").execute()
    return {row["word"].lower() for row in response.data} if response.data else set()


# Add this function to allow users to submit blacklist suggestions
def suggest_blacklist_word(word: str, submitted_by: str = None):
    client = SupabaseClient.get_client()
    payload = {"word": word, "status": "pending"}
    if submitted_by:
        payload["submitted_by"] = submitted_by  # must match uuid if used
    response = client.table("blacklist").insert(payload).execute()
    return response.data
