from typing import TypedDict, List

class GraphState(TypedDict):
    question: str
    chunks: List[dict]
    answer: str
    top_score:float
    chat_history:List[dict]