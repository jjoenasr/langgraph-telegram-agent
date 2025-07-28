from langchain_core.messages import HumanMessage, AIMessage, trim_messages
from langchain_core.output_parsers import StrOutputParser
from src.core.prompts import get_main_prompt, get_router_prompt, get_image_prompt
from src.schemas import RouterResponse
from src.config import settings
from src.core.tools import generate_image
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI

class AICompanionState(MessagesState):
    workflow: str
    image_path: str

def create_nodes_and_edges(llm: ChatGoogleGenerativeAI, tools: list):
    router_chain = get_router_prompt() | llm.with_structured_output(RouterResponse)
    main_chain = get_main_prompt() | llm.bind_tools(tools)
    image_chain = get_image_prompt() | llm | StrOutputParser()

    async def router_node(state):
        response: RouterResponse = await router_chain.ainvoke({"messages": state["messages"][-settings.router_messages:]})
        return {"workflow": response.response_type}

    async def convo_node(state):
        trimmed = trim_messages(state["messages"], token_counter=len, max_tokens=5, start_on="human", include_system=True)
        response = await main_chain.ainvoke(trimmed)
        return {"messages": response}

    async def image_node(state):
        prompt = await image_chain.ainvoke({"messages": state["messages"][-settings.router_messages:]})
        path = generate_image(prompt)
        if path:
            return {"image_path": path, "messages": [AIMessage(content=f"Here is the image you requested: {path}")]}
    
    def select_workflow(state):
        return "image" if state["workflow"] == "image" else "agent"

    def should_continue(state):
        last: AIMessage = state["messages"][-1]
        return "tools" if last.tool_calls else END

    return router_node, convo_node, image_node, select_workflow, should_continue

async def build_graph(llm: ChatGoogleGenerativeAI, tools: list) -> CompiledStateGraph:
    router_node, convo_node, image_node, select_workflow, should_continue = create_nodes_and_edges(llm, tools)
    tool_node = ToolNode(tools)

    builder = StateGraph(AICompanionState)
    builder.add_node("router", router_node)
    builder.add_node("agent", convo_node)
    builder.add_node("image", image_node)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "router")
    builder.add_conditional_edges("router", select_workflow)
    builder.add_conditional_edges("agent", should_continue, ["tools", END])
    builder.add_edge("tools", "agent")
    builder.add_edge("image", END)

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)
