from typing import Any, List
from fastapi import Depends, Response
from pydantic import Field
from app.utils import AppModel
from app.auth.adapters.jwt_service import JWTData
from app.auth.router.dependencies import parse_jwt_user_data
from app.stories.adapters.openai_service import OpenAIService
from ..service import Service, get_service
from . import router
import os
from dotenv import load_dotenv


load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai_service = OpenAIService(api_key=openai_api_key)


class CreateStoryResponse(AppModel):
    inserted_id: Any = Field(alias="_id")
    generated_story: str


@router.post("/settings", status_code=200, response_model=CreateStoryResponse)
def create_settings(
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    # start generating a story
    watson_prompt = """
           I want you to write an introduction for your usual Sherlock Holmes stories.
           Do not forget to mention what Sherlock is doing in his apartment.
            """
    user = openai_service.create_new_user(user_id=jwt_data.user_id)
    settings = openai_service.generate_watson_text(user=user, task=watson_prompt)

    inserted_id = svc.repository.create_story(
        user_id=jwt_data.user_id,
        content=settings,
        title="The Adventures of Sherlock Holmes: AI edition",
    )

    return CreateStoryResponse(inserted_id=inserted_id, generated_story=str(settings))


class CreateChatRequest(AppModel):
    message: str = Field(
        default="You may greet Sherlock Holmes and chat with him on any topic."
    )


class CreateChatResponse(AppModel):
    sherlock_message: str


@router.post("/chat", status_code=200, response_model=CreateChatResponse)
def chatting(
    input: CreateChatRequest,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    # start generating a story
    user = openai_service.get_user(user_id=jwt_data.user_id)
    watson_prompt = "What is Sherlock Holmes doing? Answer me in 1 sentence. Don't be specific, don't mention the address."
    action = openai_service.generate_watson_text(user=user, task=watson_prompt)
    print(f"action: {action}")

    prompt = f"""
        {action}
        My first sentence is {input.message}.
            """
    response = openai_service.generate_sherlock_text(user=user, task=prompt)
    return CreateChatResponse(sherlock_message=str(response))
