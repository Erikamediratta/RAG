from langgraph.graph import StateGraph, START, END
from .state import GraphState
from .orchestrator import orchestrator_node

graph = StateGraph(GraphState)
graph.add_node("orchestrator", orchestrator_node)

graph.add_edge(START, "orchestrator")
graph.add_edge("orchestrator", END)

compiled_graph = graph.compile()
