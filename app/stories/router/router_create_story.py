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
    answer: str = Field(default="London")


class CreateStoryResponse(AppModel):
    # id: Any = Field(alias="_id")
    inserted_id: Any = Field(alias="_id")
    generated_story: str



@router.post("/q1", status_code=201, response_model=CreateStoryResponse)
def create_part_1(
    input: CreateStoryQ1Request,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    # Generate story using OpenAI
    prompt = f"""1. Where did the crime take place?\n{input.answer}"""
    generated_story = openai_service.generate_text(prompt)
    
    inserted_id = svc.repository.create_story(
        user_id=jwt_data.user_id, content=generated_story
    )

    return CreateStoryResponse(inserted_id=inserted_id, generated_story=str(generated_story))

class CreateStoryQ2Request(AppModel):
    story_id: Any = Field(alias="_id")
    answer: str = Field(default="London")

@router.post("/q2")
def create_part_2(
    input: CreateStoryQ2Request,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):  
    # Generate story using OpenAI
    prompt = f"""2. How did Sherlock Holmes learn about the case?\n{input.answer}"""
    generated_story = openai_service.generate_text(prompt)
    
    update = svc.repository.add_another_part(
        user_id=jwt_data.user_id, story_id=input.story_id, content=generated_story
    ) 

    return CreateStoryResponse(inserted_id=input.story_id, generated_story=str(generated_story))

@router.post("/q3")
def create_part_3(
    input: CreateStoryQ2Request,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):  
    # Generate story using OpenAI
    prompt = f"""3. Who was the victim? What was the primary evidence found at the crime scene?\n{input.answer}"""
    generated_story = openai_service.generate_text(prompt)
    
    update = svc.repository.add_another_part(
        user_id=jwt_data.user_id, story_id=input.story_id, content=generated_story
    ) 

    return CreateStoryResponse(inserted_id=input.story_id, generated_story=str(generated_story))


@router.post("/q4")
def create_part_4(
    input: CreateStoryQ2Request,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):  
    # Generate story using OpenAI
    prompt = f"""4. Who should be the new character that could tell Sherlock more about the case?\n{input.answer}"""
    generated_story = openai_service.generate_text(prompt)
    
    update = svc.repository.add_another_part(
        user_id=jwt_data.user_id, story_id=input.story_id, content=generated_story
    ) 

    return CreateStoryResponse(inserted_id=input.story_id, generated_story=str(generated_story))

