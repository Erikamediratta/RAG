from db import supabase

result=supabase.table("sops").select("*").execute()
print(len(result.data))