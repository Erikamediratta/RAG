import os 

from dotenv import load_dotenv
load_dotenv()
from pinecone import Pinecone
from embeddings import generate_embedding

pc=Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index=pc.Index(os.environ["PINECONE_INDEX_NAME"])

from embeddings import generate_embedding

def get_chunks(user_question, chunk_count=8):
    user_query=generate_embedding(user_question)

    result=index.query(
        vector=user_query,
        top_k=chunk_count,
        include_metadata=True
    )


    chunks=[]
    for match in result["matches"]:
        chunks.append({
            "document_name": match["metadata"]["document_name"],
            "chunk_text": match["metadata"]["chunk_text"],
            "similarity": match["score"]
        })
    return chunks
def router_node(state):
    chunks = get_chunks(state["question"])
    top_score=chunks[0]["similarity"] if chunks else 0
    return {"chunks": chunks,"top_score":top_score}