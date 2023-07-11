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


class GetStoryResponse(AppModel):
    story: Any


@router.get("/{story_id:str}", status_code=200, response_model=GetStoryResponse)
def get_story(
    story_id: str,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    # start generating a story
    story = svc.repository.get_story(user_id=jwt_data.user_id, story_id=story_id)

    return GetStoryResponse(story=story)
