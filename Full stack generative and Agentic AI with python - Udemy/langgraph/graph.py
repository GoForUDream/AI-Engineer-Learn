from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langgraph.prebuilt import ToolNode

from state import State
from llm import llm
from tools import calculator

# Bind tool to the LLM
llm_with_tools = llm.bind_tools([calculator])


def route_tools(state: State):
    """Determine if the user message is a tool request or a normal chat message."""

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


# Chatbot Node
def chatbot(state: State):
    """Read the message from the state, send to LLM and return generate response"""

    response = llm_with_tools.invoke(state["messages"])

    return {"messages": [response]}


# Initialize the StateGraph
builder = StateGraph(State)

# Tool Node
tool_node = ToolNode([calculator])

# Add Notes
builder.add_node("chatbot", chatbot)
builder.add_node("tools", tool_node)

# Add edges
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", route_tools)
builder.add_edge("tools", "chatbot")

# Complie the graph
graph = builder.compile()
