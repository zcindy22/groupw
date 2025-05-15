import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICEKEY = os.getenv("SUPABASE_SERVICEKEY")

class SupabaseClient:
    _instance: Client = None
    _service_client: Client = None 

    @classmethod
    def get_client(cls):
        if cls._instance is None:
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise ValueError("Supabase credentials not found in environment.")
            cls._instance = create_client(SUPABASE_URL, SUPABASE_KEY)
        return cls._instance
    
    @classmethod
    def get_service_client(cls) -> Client:
        if cls._service_client is None:
            if not SUPABASE_URL or not SUPABASE_SERVICEKEY:
                raise ValueError("Supabase service credentials not found in environment.")
            cls._service_client = create_client(SUPABASE_URL, SUPABASE_SERVICEKEY)
        return cls._service_client
