from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from telegram import Bot
from src.config import settings
from src.core.agent_manager import Agent
from src.schemas import ChatRequest
from src.logger_config import logger
import base64
import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

# Initialize the Telegram Bot with the token from settings
bot = Bot(settings.telegram_bot_token)

# Initialize the agent
agent = Agent()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await agent.initialize_agent()
    yield

app = FastAPI(lifespan=lifespan) 

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/webhook")
async def webhook(request: Request):
    # Process the incoming webhook request
    update = await request.json()
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        workflow, msg, image_path = await agent.answer(text, chat_id)

        if workflow == "image" and image_path:
            # Send the generated image back to the user
            with open(image_path, "rb") as img_file:
                await bot.send_photo(chat_id=chat_id, photo=img_file)
                logger.info(f"Sent image to chat {chat_id}")

        elif workflow == "conversation":
            # Send the text response back to the user
            await bot.send_message(chat_id=chat_id, text=msg)
            logger.info(f"Sent message to chat {chat_id}: {msg[:50]}...")
    
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: ChatRequest):
    # This endpoint can be used to test the agent via a web interface or other means
    user_message = request.prompt.strip()
    workflow, msg, image_path = await agent.answer(user_message, "test_chat_id")

    if workflow == "image" and image_path:
        with open(image_path, "rb") as img_file:
            return {"image": base64.b64encode(img_file.read()).decode('utf-8')}
    elif workflow == "conversation":
        return {"response": msg}

    return {"error": "Unknown workflow"}

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", log_level="info", reload=False)