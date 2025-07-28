from langchain_core.tools import tool
from ddgs import DDGS
from src.logger_config import logger
from langchain_mcp_adapters.client import MultiServerMCPClient
from together import Together
from uuid import uuid4
from typing import Optional
import base64
from src.config import settings

@tool
def web_search(query: str) -> str:
    """Search the web for information"""
    try:
        results = DDGS().text(query, max_results=8)
        if len(results) == 0:
            raise ValueError("No results found! Try a less restrictive/shorter query.")
        postprocessed_results = [f"[{result['title']}]({result['href']})\n{result['body']}" for result in results]
        return "## Search Results\n\n" + "\n\n".join(postprocessed_results)
    except Exception as e:
        logger.error(f"Web search tool error: {e}")
        return f"Error searching the web: {str(e)[:100]}..."
    

def generate_image(prompt: str, model: str = "black-forest-labs/FLUX.1-schnell-Free") -> Optional[str]:
    """Generate an image based on a prompt using Together AI."""
    try:
        together_client = Together(api_key=settings.together_api_key)
        response = together_client.images.generate(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",
            width=1024,
            height=768,
            steps=4,
            n=1,
            response_format="b64_json"
        )
        if not response or not response.data or not response.data[0].b64_json:
            print("No image generated or response is empty.")
            return None
        img_data = base64.b64decode(response.data[0].b64_json)
        img_path = f"data/generated_image_{uuid4().hex}.png"
        with open(img_path, "wb") as img_file:
            img_file.write(img_data)
        return img_path
    
    except Exception as e:
        logger.error(f"Image generation error: {str(e)[:100]}...")
        return None

async def get_mcp_tools() -> list:
    """Get tools from the MCP server"""
    servers = {
        "slack": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-slack"],
            "env": {
                "SLACK_BOT_TOKEN": settings.slack_bot_token,
                "SLACK_TEAM_ID": settings.slack_team_id
            },
            "transport": "stdio"
        },
    }
    try:
        client = MultiServerMCPClient(servers)
        tools = await client.get_tools()
        return tools
    except Exception as e:
        logger.error(f"Error fetching tools from MCP: {str(e)[:100]}")
        return []