import os 
from db import supabase

from embeddings import generate_embedding

def get_chunks(user_question, chunk_count=8):
    user_query=generate_embedding(user_question)

    result=supabase.rpc("match",{
        "query_embedding":user_query,
       "match_count":chunk_count
    }).execute()

    return result.data
def router_node(state):
    chunks = get_chunks(state["question"])
    top_score=chunks[0]["similarity"] if chunks else 0
    return {"chunks": chunks,"top_score":top_score}