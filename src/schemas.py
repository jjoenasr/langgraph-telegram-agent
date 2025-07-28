from pydantic import BaseModel, Field
from typing import Literal

class RouterResponse(BaseModel):
    response_type: Literal['conversation', 'image'] = Field(
        description="The response type to give to the user. It must be one of: 'conversation' or 'image'"
    )

class ChatRequest(BaseModel):
    prompt: str