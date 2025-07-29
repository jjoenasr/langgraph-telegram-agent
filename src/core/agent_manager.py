from langchain_core.messages import HumanMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.tools import web_search, get_mcp_tools
from typing import Optional
from src.core.builder import build_graph
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from src.logger_config import logger
from src.config import settings

class Agent:
    def __init__(self):
        logger.info("AI Agent initialized.")
        if not settings.google_api_key:
            logger.error("Missing Google API Key")
            raise ValueError("Missing Google API Key")
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
        self.tools = []
        self.agent = None
        
    async def initialize_agent(self, checkpointer: Optional[AsyncSqliteSaver | MemorySaver] = None):
        self.tools = [web_search]
        self.tools.extend(await get_mcp_tools())
        if not checkpointer:
            checkpointer = MemorySaver()
        self.agent = await build_graph(self.llm, self.tools, checkpointer)
    
    async def load_prev_messages(self, thread_id: str) -> list[BaseMessage]:
        """Load agent messages"""
        config = {"configurable": {"user_id": "user-xxx", "thread_id": thread_id}}
        logger.info(f"New session started, thread_id: {thread_id}")
        msgs = []
        try:
            state = await self.agent.aget_state(config)
            msgs = state.values.get('messages', [])
        except Exception as e:
            logger.error(f"Error loading prev messages: {str(e)}")
        return msgs

    
    async def answer(self, question: str, thread_id: str,) -> tuple[str, str, Optional[str]]:
        """Answer a question directly using the agent"""
        if not question.strip():
            return "You can't send an empty message"
        logger.info(f"Agent received question: {question[:50]}...")
        config = {"configurable": {"user_id": "user-xxx", "thread_id": thread_id}}
        llm_output = await self.agent.ainvoke({"messages": [HumanMessage(content=question)]}, config=config)
        workflow = llm_output.get('workflow', 'conversation')
        last_msg = llm_output['messages'][-1].content
        image_path = llm_output.get('image_path', None)
        logger.info(f"Agent answers: {last_msg[:50]}...")
        return workflow, last_msg, image_path