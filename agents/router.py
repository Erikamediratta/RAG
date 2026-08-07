import os
from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from embeddings import generate_embedding
from qdrant_client.models import Filter,FieldCondition,MatchValue

client = QdrantClient(
    url=os.environ["QDRANT_URL_NAME"],
    api_key=os.environ["QDRANT_API_KEY"]
)


def get_chunks(user_question, chunk_count=8,document_filter=None):
    user_query = generate_embedding(user_question)

    qdrant_filter=None
    if document_filter:
        qdrant_filter=Filter(
            must=[FieldCondition(key="document_name",match=MatchValue(value=document_filter))]
        )
    results = client.query_points(
        collection_name="documents",
        query=user_query,
        limit=chunk_count,
        with_payload=True,
        query_filter=qdrant_filter
    ).points

    chunks = []
    for point in results:
        chunks.append({
            "document_name": point.payload["document_name"],
            "chunk_text": point.payload["chunk_text"],
            "similarity": point.score
        })
    return chunks


def router_node(state):
    chunks = get_chunks(state["question"],document_filter=state.get("document_filter"))
    top_score = chunks[0]["similarity"] if chunks else 0
    return {"chunks": chunks, "top_score": top_score}


