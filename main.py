from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from agents.graph import compiled_graph
from db import supabase
from fastapi import UploadFile, File
import shutil
#shutil is python library to copy an uploaded file's contents to disk
from ingestion import ingest_documents
from pinecone import Pinecone
import os
pc=Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index=pc.index(os.environ["PINECONE_INDEX_NAME"])
app=FastAPI()


@app.post("/api/chat")
def chat(data:dict):
    result=compiled_graph.invoke({"question":data["message"],"chat_history":data.get("chat_history",[])})
    return {"response":result["answer"]}


@app.get("/api/documents")
def list_documents():
    result = supabase.table("documents").select("*").execute()
    return {"documents": result.data}

@app.post("/api/documents")
async def create_document(file: UploadFile = File(...)):
    file_path = f"pdfs/{file.filename}"
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    chunk_count = ingest_documents(file_path, file.filename, index, supabase)
    return {"status": "success", "document_name": file.filename, "chunks_added": chunk_count}

app.mount("/",StaticFiles(directory="static",html=True),name="static")
