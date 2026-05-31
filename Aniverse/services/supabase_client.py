import os
# from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_url = os.getenv("SUPABASE_URL", "")
_anon_key = os.getenv("SUPABASE_ANON_KEY", "")
_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# Public client — respects RLS policies
# supabase: Client = create_client(_url, _anon_key)
supabase = None

# Admin client — bypasses RLS (use only in admin routes)
# supabase_admin: Client = create_client(_url, _service_key)
supabase_admin = None


def get_authed_client(access_token: str):
    """Returns a Supabase client authenticated as the current user."""
    # client = create_client(_url, _anon_key)
    # client.auth.set_session(access_token, "")
    # return client
    return None
