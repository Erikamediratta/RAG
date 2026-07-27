from langgraph.graph import StateGraph, START, END
from .state import GraphState
from .router import router_node
from .sub_agent import sub_agent_node
from .tool_agent import tool_agent_node

def decide_next(state):
    if state["top_score"]<0.72:
        return "tool_agent"
    return "sub_agent"
graph = StateGraph(GraphState)
graph.add_node("router", router_node)
graph.add_node("sub_agent", sub_agent_node)
graph.add_node("tool_agent",tool_agent_node)


graph.add_edge( START,"router")
graph.add_conditional_edges("router",decide_next,{
    "sub_agent":"sub_agent",
    "tool_agent":"tool_agent"
})
graph.add_edge("sub_agent",END)
graph.add_edge("tool_agent", END)

compiled_graph = graph.compile()


