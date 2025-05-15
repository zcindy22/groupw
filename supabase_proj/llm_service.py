# supabase_proj/llm_service.py

import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def correct(text: str):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.0,
            messages=[
                {"role": "system", "content": "You are a grammar assistant. Return only a JSON array of {id, start, end, suggestion}."},
                {"role": "user", "content": text},
            ],
        )
        suggestions = json.loads(response.choices[0].message.content.strip())
        return [{
            "id": str(s["id"]),
            "start": int(s["start"]),
            "end": int(s["end"]),
            "suggestion": s["suggestion"]
        } for s in suggestions]
    except Exception as e:
        print("LLM error:", e)
        return []

def feedback(user_id: str, suggestion_id: str, action: str, reason: str = ""):
    from supabase_proj.client import SupabaseClient
    client = SupabaseClient.get_client()
    client.table("feedback").insert({
        "username": user_id,
        "suggestion_id": suggestion_id,
        "action": action,
        "reason": reason
    }).execute()
