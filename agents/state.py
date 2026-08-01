from typing import TypedDict, List

class GraphState(TypedDict):
    question: str
    answer: str
    chat_history: List[dict]
    decision_trace: List[dict]