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


# class CreateStoryResponse(AppModel):
#     inserted_id: Any = Field(alias="_id")
#     generated_story: str


# @router.post("/settings", status_code=200, response_model=CreateStoryResponse)
# def create_settings(
#     jwt_data: JWTData = Depends(parse_jwt_user_data),
#     svc: Service = Depends(get_service),
# ):
#     # start generating a story
#     watson_prompt = """
#             I want you to act as Dr. Watson. 
#             Write in two paragraphs.
#             Describe what you are doing in the apartment.
#             Also include what is Sherlock Holmes involved in 
#             (choose one from his usual activities, except solving the crime.)
#             Use I, instead of Dr. Watson. Don't say I, Dr. Watson.
#             """
#     user = openai_service.create_new_user(user_id=jwt_data.user_id)
#     settings = openai_service.generate_text(user=user, task=watson_prompt)

#     inserted_id = svc.repository.create_story(
#         user_id=jwt_data.user_id,
#         content=settings,
#         title="The Adventures of Sherlock Holmes: AI edition",
#     )

#     return CreateStoryResponse(inserted_id=inserted_id, generated_story=str(settings))


# class CreateStoryRequest(AppModel):
#     story_id: str
#     q1: str = Field(
#         default="You may greet Sherlock Holmes and ask about his activities."
#     )


# @router.post("/respond_1_sherlock", status_code=200, response_model=CreateStoryResponse)
# def create_respond_1_sherlock(
#     input: CreateStoryRequest,
#     jwt_data: JWTData = Depends(parse_jwt_user_data),
#     svc: Service = Depends(get_service),
# ):
#     # generate respond to Watson
#     sherlock_prompt = f"""
#             I want you to act as Sherlock Holmes. 
#             Answer to your friend, Dr. Watson, who said 
#             “{input.q1}“ in your usual manner.
#             """
#     user = openai_service.get_user(user_id=jwt_data.user_id)
#     respond_1 = openai_service.generate_text(user=user, task=sherlock_prompt)
#     update = svc.repository.add_another_part(
#         user_id=jwt_data.user_id,
#         story_id=input.story_id,
#         content=respond_1,
#     )

#     return CreateStoryResponse(
#         inserted_id=input.story_id, generated_story=str(respond_1)
#     )

# @router.post("/respond_2_sherlock", status_code=200, response_model=CreateStoryResponse)
# def create_respond_1_sherlock(
#     input: CreateStoryRequest,
#     jwt_data: JWTData = Depends(parse_jwt_user_data),
#     svc: Service = Depends(get_service),
# ):
#     # generate respond to Watson
#     sherlock_prompt = f"""
#             I want you to act as Sherlock Holmes. 
#             Answer to your friend, Dr. Watson, who said 
#             “{input.q1}“ in your usual manner.
#             """
#     user = openai_service.get_user(user_id=jwt_data.user_id)
#     respond_1 = openai_service.generate_text(user=user, task=sherlock_prompt)
#     update = svc.repository.add_another_part(
#         user_id=jwt_data.user_id,
#         story_id=input.story_id,
#         content=respond_1,
#     )

#     return CreateStoryResponse(
#         inserted_id=input.story_id, generated_story=str(respond_1)
#     )
