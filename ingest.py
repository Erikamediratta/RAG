import os
import time
from dotenv import load_dotenv

load_dotenv()

from db import supabase
from pdf_extract import extract
from text_splitter import split_documents
from embeddings import generate_embedding
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

client = QdrantClient(
    url=os.environ["QDRANT_URL_NAME"],
    api_key=os.environ["QDRANT_API_KEY"]
)


pdf_folder = "pdfs"

def upsert_with_retry(points,max_retries=3):
    for attempt in range(max_retries):
        try:
            client.upsert(collection_name="documents",points=points)

            return
        except Exception as e:
            print(f"Upsert failed :{e}")
            time.sleep(3)
    print(f"Failed after {max_retries} attempts")


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
        embedding = generate_embedding(chunk.page_content)

        point = PointStruct(
            id=i + hash(file) % 1000000000,
            vector=embedding,
            payload={
                "document_name": chunk.metadata["source"],
                "chunk_text": chunk.page_content,
                "chunk_index": i,
            }
        )
        upsert_with_retry([point])


        if i % 100 == 0:
            print(f"  Inserted chunk {i}/{len(chunks)}")

    print(f"Done with file, {file}")

    

