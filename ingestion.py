from pdf_extract import extract
from embeddings import generate_embedding
from text_splitter import split_documents

def ingest_documents(pdf_path,filename,index,supabase):
    text=extract(pdf_path)
    #split documents
    chunks=split_documents(text,filename)

    for i,chunk_item in enumerate(chunks):
        embedding=generate_embedding(chunk_item.page_content)
        index.upsert(vectors=[{
            "id":f"{filename}-chunk-{i}",
            "values":embedding,
            "metadata":{
                "document_name":chunk_item.metadata["source"],
                "chunk_text":chunk_item.page_content,
                "chunk_index":i
            }
        }])
    supabase.table("documents").insert({
        "document_name":filename,
        "chunk_count":len(chunks)
    }).execute()

    return len(chunks)