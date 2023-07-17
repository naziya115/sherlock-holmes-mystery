from typing import Any
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


class CreateStoryQ1Request(AppModel):
    answer: str = Field(default="Where did the crime take place?")


class CreateStoryResponse(AppModel):
    inserted_id: Any = Field(alias="_id")
    generated_story: str
    next_question: str


@router.post("/q1", status_code=200, response_model=CreateStoryResponse)
def create_part_1(
    input: CreateStoryQ1Request,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    # start generating a story
    prompt = f"""{input.answer}."""
    user = openai_service.create_new_user(user_id=jwt_data.user_id)

    generated_story = openai_service.generate_text(user=user, answer=prompt)
    inserted_id = svc.repository.create_story(
        user_id=jwt_data.user_id, content=generated_story, title=""
    )

    next_question = openai_service.generate_next_question(prev_story=generated_story)

    return CreateStoryResponse(
        inserted_id=inserted_id,
        generated_story=str(generated_story),
        next_question=str(next_question),
    )


class CreateStoryQ2Request(AppModel):
    story_id: Any = Field(alias="_id")
    answer: str = Field(default="London")
    next_question: str = Field(default="What was the question? ")


@router.post("/q2")
def create_part_2(
    input: CreateStoryQ2Request,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    # generate the continuation of the story
    prompt = f"""{input.answer}."""
    user = openai_service.get_user(user_id=jwt_data.user_id)
    generated_story = openai_service.generate_text(user=user, answer=prompt)
    update = svc.repository.add_another_part(
        user_id=jwt_data.user_id,
        story_id=input.story_id,
        content=generated_story,
    )

    # generate next question
    next_question = openai_service.generate_next_question(prev_story=generated_story)

    return CreateStoryResponse(
        inserted_id=input.story_id,
        generated_story=str(generated_story),
        next_question=str(next_question),
    )


@router.post("/q3")
def create_part_3(
    input: CreateStoryQ2Request,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    # generate the continuation of the story
    prompt = f"""{input.answer}. Make the generated story in a conversation format."""
    user = openai_service.get_user(user_id=jwt_data.user_id)
    generated_story = openai_service.generate_text(user=user, answer=prompt)
    update = svc.repository.add_another_part(
        user_id=jwt_data.user_id,
        story_id=input.story_id,
        content=generated_story,
    )

    # generate next question
    next_question = openai_service.generate_next_question(prev_story=generated_story)

    return CreateStoryResponse(
        inserted_id=input.story_id,
        generated_story=str(generated_story),
        next_question=str(next_question),
    )


@router.post("/q4")
def create_part_4(
    input: CreateStoryQ2Request,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    # generate the continuation of the story
    prompt = f"""{input.answer}. End the story with a very witty ending. Use Sherlock Holmes's deductive skills."""
    user = openai_service.get_user(user_id=jwt_data.user_id)
    generated_story = openai_service.generate_text(user=user, answer=prompt)
    update = svc.repository.add_another_part(
        user_id=jwt_data.user_id,
        story_id=input.story_id,
        content=generated_story,
    )

    title = openai_service.generate_title(generated_story)
    svc.repository.update_title(
        title=title, user_id=jwt_data.user_id, story_id=input.story_id
    )

    return CreateStoryResponse(
        inserted_id=input.story_id,
        generated_story=str(generated_story),
        next_question="",
    )
