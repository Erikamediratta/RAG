import os
import time
from dotenv import load_dotenv

load_dotenv()

from db import supabase
from pdf_extract import extract
from text_splitter import split_documents
from embeddings import generate_embedding

pdf_folder = "pdfs"



for file in os.listdir(pdf_folder):
    pdf_path = os.path.join(pdf_folder, file)

    # upload the pdf to the bucket
    with open(pdf_path, "rb") as f:
        supabase.storage.from_("sop-bucket").upload(
            file, f, {"upsert": "true"}
        )
    # extract text from pdf
    text = extract(pdf_path)
    print(f"Extracted {len(text)} chaacters from {file}")

    # chunking of the extracted text
    chunks = split_documents(text, file)
    print(f"Chunked into {len(chunks)}")



    # generate embeddings for each chunk and insert it
    for i, chunk in enumerate(chunks):
        print(f"  Embedding chunk {i}...")
        try:
            embedding = generate_embedding(chunk.page_content)

        except Exception as e:
            print(f"  ERROR on chunk {i}: {e}")
            break

        supabase.table("document_chunks").insert({
            "document_name": chunk.metadata["source"],
            "chunk_text": chunk.page_content,
            "chunk_index": i,
            "embedding": embedding,
            "storage_path": file
        }).execute()

        if i % 100 == 0:
            print(f"  Inserted chunk {i}/{len(chunks)}")

    print(f"Done with file, {file}")
    break
    

