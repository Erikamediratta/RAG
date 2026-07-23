from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from agents.graph import compiled_graph

app=FastAPI()

@app.post("/api/chat")
def chat(data:dict):
    result=compiled_graph.invoke({"question":data["message"],"chat_history":data.get("chat_history",[])})
    return {"response":result["answer"]}

app.mount("/",StaticFiles(directory="static",html=True),name="static")
