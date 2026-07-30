import os
from dotenv import load_dotenv
load_dotenv()

from google import genai

client=genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def generate_answer(question,chunks,chat_history=None):
    context=""
    for c in chunks:
        context=context+ c["chunk_text"]
    history_text=""
    if chat_history:
        for chat in chat_history:
            history_text=history_text + f"{chat['role']}:{chat['content']}\n"

    prompt=f"""You are a helpful assistant answering the user's question based on the technical documentation,
    Previous Conversation:
    {history_text}
    Context for the Documentation:
    {context}
    User's Question:
    {question}
    Answer the user's question in detail,only based on the information provided in the context.Explain concepts thoroughly,include relevant specifics from the context (definitions, components, examples, or steps where available), and aim for a comprehensive response rather than a brief summary.
    """
    result=client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,

    )
    return result.text

def sub_agent_node(state):
    answer = generate_answer(state["question"], state["chunks"],state["chat_history"])
    
    return {"answer": answer}

# if __name__ == "__main__":
#     from .router import get_chunks
#     chunks = get_chunks("How does chrome.storage.local work?")
#     answer = generate_answer("How does chrome.storage.local work?", chunks)
#     print(answer)

