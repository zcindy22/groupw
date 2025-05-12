# supabase/db_utils.py
from supabase_proj.client import SupabaseClient
from typing import Literal

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

def get_token_balance(user_id: str) -> int:
    """
    Read the current token balance for a given user_id.
    """
    client = SupabaseClient.get_client()
    resp = (
        client
        .table("users").select("tokens").eq("id", user_id).single().execute())
    if resp.error:
        raise RuntimeError(f"Error fetching tokens: {resp.error.message}")
    return int(resp.data.get("tokens", 0))

def adjust_tokens(user_id: str, delta: int) -> int:
    client = SupabaseClient.get_client()

    # 1) Fetch current balance
    current_resp = (
        client
        .table("users").select("tokens").eq("id", user_id).single().execute())
    if current_resp.error:
        raise RuntimeError(f"Error fetching tokens: {current_resp.error.message}")
    current = current_resp.data.get("tokens", 0)

    # 2) Compute and validate new balance
    new_balance = current + delta
    if new_balance < 0:
        raise ValueError(f"Insufficient tokens: have {current}, need {-delta}")

    # 3) Write updated balance back
    update_resp = (
        client
        .table("users").update({"tokens": new_balance}).eq("id", user_id).execute())
    if update_resp.error:
        raise RuntimeError(f"Error updating tokens: {update_resp.error.message}")

    return new_balance

def charge_for_action(
    user_id: str,
    action: Literal[
        "self_edit",
        "llm_accept",
        "llm_reject",
        "share_reject",
        "save_file",
        "error_free_bonus"
    ],
    **context
    ) -> int:
    """
    Charge or award tokens based on a named action.
    Returns the new balance.
    """
    if action == "self_edit":
        words = context.get("words_changed", 0)
        cost = -(words // 2)
    elif action == "llm_accept":
        cost = -1
    elif action == "llm_reject":
        cost = -5
    elif action == "share_reject":
        cost = -3
    elif action == "save_file":
        cost = -5
    elif action == "error_free_bonus":
        cost = +3
    else:
        raise ValueError(f"Unknown token action: {action}")

    return adjust_tokens(user_id, cost)


def submit_blacklist_word(user_id: str, word: str) -> dict:
    client = SupabaseClient.get_client()
    resp = client.table("blacklist") \
                 .insert({
                   "word":          word,
                   "submitted_by":  user_id,
                   "status":        "pending"
                 }) \
                 .execute()

    # Supabase-py v2 returns a PostgrestResponse, not APIResponse
    if not resp.data:
        raise RuntimeError("Blacklist insert returned no data")
    return resp.data[0]  # the newly created row


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
