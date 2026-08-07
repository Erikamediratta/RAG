from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from agents.graph import compiled_graph
from db import supabase
from fastapi import UploadFile, File,Form
import shutil
#shutil is python library to copy an uploaded file's contents to disk
from ingestion import ingest_documents

import os
from qdrant_client import QdrantClient
client = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])
app=FastAPI()


@app.post("/api/chat")
def chat(data:dict):
    result=compiled_graph.invoke({"question":data["message"],"chat_history":data.get("chat_history",[]),"document_filter":data.get("document_filter")})
    return {"response":result["answer"],"decision_trace":result.get("decision_trace",[])}


@app.get("/api/documents")
def list_documents(user_id:str=None):
    query=supabase.table("documents").select("*")
    if user_id:
        query=query.eq("user_id",user_id)

    result=query.execute()
    return {"documents": result.data}

@app.post("/api/documents")
async def create_document(file: UploadFile = File(...)):
    file_path = f"pdfs/{file.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunk_count = ingest_documents(file_path, file.filename, client, supabase)
    return {"status": "success", "document_name": file.filename, "chunks_added": chunk_count}

from ingestion import embed_document

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...),user_id:str= Form(...)):
    os.makedirs("pdfs", exist_ok=True)
    file_path = f"pdfs/{file.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    supabase.table("documents").upsert({
        "document_name": file.filename,
        "chunk_count": 0,
        "status": "uploaded",
        "user_id": user_id
    }, on_conflict="document_name").execute()

    return {"status": "success", "document_name": file.filename}


@app.post("/api/documents/{document_name}/embed")
def embed_document_endpoint(document_name: str):
    os.makedirs("pdfs", exist_ok=True)
    file_path = f"pdfs/{document_name}"
    chunk_count = embed_document(file_path, document_name, client, supabase)
    return {"status": "embedded", "document_name": document_name, "chunks_added": chunk_count}
app.mount("/",StaticFiles(directory="static",html=True),name="static")

