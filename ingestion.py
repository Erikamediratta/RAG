from pdf_extract import extract
from embeddings import generate_embedding
from text_splitter import split_documents
from qdrant_client.models import PointStruct


def ingest_documents(pdf_path, filename, client, supabase):
    text = extract(pdf_path)
    chunks = split_documents(text, filename)

    for i, chunk_item in enumerate(chunks):
        embedding = generate_embedding(chunk_item.page_content)

        point = PointStruct(
            id=i + hash(filename) % 1000000000,
            vector=embedding,
            payload={
                "document_name": chunk_item.metadata["source"],
                "chunk_text": chunk_item.page_content,
                "chunk_index": i,
            }
        )
        client.upsert(collection_name="documents", points=[point])

    supabase.table("documents").insert({
        "document_name": filename,
        "chunk_count": len(chunks)
    }).execute()

    return len(chunks)