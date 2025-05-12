# supabase_proj/llm_service.py
import os
from supabase_proj.client import SupabaseClient
from typing import List, Dict

# Feature‐flag: "dryrun" until you wire up the real API
PROVIDER = os.getenv("LLM_PROVIDER", "dryrun")
'''
def correct(text: str) -> List[Dict]:
    """
    Returns a list of correction suggestions, each a dict:
      { "id": str, "start": int, "end": int, "suggestion": str }
    In dryrun mode, returns [] so UI can be built first.
    """
    if PROVIDER == "dryrun":
        return []
    return _correct_remote(text)
'''

def correct(text: str) -> List[Dict]:
    if PROVIDER == "dryrun":
        return [
            { "id": "1", "start": 0, "end": min(4, len(text)), "suggestion": "TEST" },
            { "id": "2", "start": min(5,len(text)), "end": min(10,len(text)), "suggestion": "MOCK" }
        ]
    return _correct_remote(text)


def feedback(username: str, suggestion_id: str, action: str, reason: str = "") -> None:
    """
    Record the user’s Accept/Reject action for admin review.
    """
    client = SupabaseClient.get_client()
    # Assumes you have a "feedback" table with columns
    #   username, suggestion_id, action, reason
    client.table("feedback").insert({
        "username": username,
        "suggestion_id": suggestion_id,
        "action": action,
        "reason": reason
    }).execute()

def _correct_remote(text: str) -> List[Dict]:
    """
    Replace this with your real LLM call (OpenAI, Vertex AI, etc.).
    Should return the same structure as the stub above.
    """
    raise NotImplementedError("Hook up your LLM here")
