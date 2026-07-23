import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase_url=os.environ["SUPABASE_URL"]
supabase_key=os.environ["SUPABASE_SERVICE_ROLE_KEY"]

supabase=create_client(supabase_url,supabase_key)
