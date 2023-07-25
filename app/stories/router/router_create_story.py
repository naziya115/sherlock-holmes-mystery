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


class CreateStoryRequest(AppModel):
    story_id: str
    sherlock_message: str = Field(default="")
    type: str = Field(default="")


class CreateStoryResponse(AppModel):
    inserted_id: Any = Field(alias="_id")
    generated_story: str


# set intro for the story
@router.post("/setting", status_code=200, response_model=CreateStoryResponse)
def create_setting(
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    watson_prompt = """
           'Write an introduction for your usual Sherlock Holmes stories in 100 words.
           Do not forget to mention what Sherlock is doing in his apartment.'
            """
    user = openai_service.create_new_user(user_id=jwt_data.user_id)
    settings = openai_service.generate_watson_text(user=user, task=watson_prompt)

    inserted_id = svc.repository.create_story(
        user_id=jwt_data.user_id,
        content=settings,
        title="The Adventures of Sherlock Holmes: AI edition",
    )

    return CreateStoryResponse(inserted_id=inserted_id, generated_story=str(settings))


class CreateChatResponse(AppModel):
    sherlock_message: str


# introduce the crime
@router.post("/case_intro", status_code=200, response_model=CreateStoryResponse)
def create_case_intro(
    input: CreateStoryRequest,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    watson_prompt = """
            Create a dialogue between Sherlock Holmes and a new visitor, who will describe his/her case.
            Remember to describe the visitor's appereance and be detailed about the crime that happened.
            The visitor must tell full story of what happened. 
            The visitor must name 3 individuals who are related to the crime.
            """
    user = openai_service.get_user(user_id=jwt_data.user_id)
    case_intro = openai_service.generate_watson_text(user=user, task=watson_prompt)

    inserted_id = svc.repository.add_another_part(
        user_id=jwt_data.user_id,
        story_id=input.story_id,
        content=case_intro,
    )

    return CreateStoryResponse(
        inserted_id=input.story_id, generated_story=str(case_intro)
    )


# chat with sherlock holmes
@router.post("/chat", status_code=200, response_model=CreateChatResponse)
def chatting(
    input: CreateStoryRequest,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    user = openai_service.get_user(user_id=jwt_data.user_id)
    watson_prompt = "What is Sherlock Holmes doing? Answer me in 1 sentence. Don't be specific, don't mention the address."
    action = openai_service.generate_watson_text(user=user, task=watson_prompt)

    if input.type == "small_talk":
        prompt = f"""
            {action}
            My first sentence is {input.sherlock_message}.
                """
        response = openai_service.generate_sherlock_text(user=user, task=prompt)
    else:
        prompt = f"""
            Answer to questions about the case. 
            Be specific. Respond in 1 sentence. Your answers must be short but clear.
            Do not use your name in a response.
                """
        response = openai_service.generate_sherlock_text(user=user, task=prompt)

    inserted_id = svc.repository.add_another_part(
        user_id=jwt_data.user_id,
        story_id=input.story_id,
        content='"' + input.sherlock_message + '"' '$\n"' + response + '"$\n',
    )

    return CreateChatResponse(sherlock_message=str(response))


# get main suspected individuals for answer choices
@router.get("/main_suspects", status_code=200, response_model=CreateChatResponse)
def get_main_suspects(
    jwt_data: JWTData = Depends(parse_jwt_user_data),
):
    user = openai_service.get_user(user_id=jwt_data.user_id)
    watson_prompt = """Who do you think can be the main suspects in this case from the story the vistitor desribed?
    You must use names of individuals or their description, for example: "a thief". Do not write any explanations or descriptions.
    You have to think of exactly 3 suspects from the visitor's story!
    Format your answer: 1. individual, 2. individual, 3. individual
    """
    main_suspects = openai_service.generate_watson_text(user=user, task=watson_prompt)

    return CreateChatResponse(sherlock_message=str(main_suspects))


# generate investigation of the case
@router.post("/investigation", status_code=200, response_model=CreateStoryResponse)
def create_case_investigation(
    input: CreateStoryRequest,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    watson_prompt = """
           Write a full investigation for the case that the visitor described above.
           Describe details of the location that you and Sherlock went to. 
           Describe all related to the case evidence.
           Include your dialogue with Sherlock Holmes.
           Do not disclose the resolution of the crime.
           Finish the investigation of the crime on a climax moment. The criminal is unknown.
           Only Sherlock Holmes can solve this mystery.
            """
    user = openai_service.get_user(user_id=jwt_data.user_id)
    investigation = openai_service.generate_watson_text(user=user, task=watson_prompt)

    inserted_id = svc.repository.add_another_part(
        user_id=jwt_data.user_id,
        story_id=input.story_id,
        content=investigation,
    )

    return CreateStoryResponse(
        inserted_id=input.story_id, generated_story=str(investigation)
    )


# unravel the solution to the case through sherlock chain
@router.post("/solution", status_code=200, response_model=CreateChatResponse)
def create_soltuion_to_case(
    input: CreateStoryRequest,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    watson_prompt = """
           Describe the visitor's story and the your and Sherlock's investigation.
           Be specific. Do not write any explanations or unrelated sentences.
           You must include all details that the visitor have said and all important evidence 
           that were found on the investigation.
           Use only 300 words.
            """
    user = openai_service.get_user(user_id=jwt_data.user_id)
    case_details = openai_service.generate_watson_text(user=user, task=watson_prompt)

    sherlock_prompt = f"""
    Use Watson's description of the case:
    {case_details}
    You need to come up with the most creative solution to this case using ONLY YOUR DEDUCTIVE METHODS.
    Identify the criminal, choose one from the story, and 
    find an explanation and a motive with which he/she committed the crime.
    Be specific. In your explanation, you must explain your deductive methods 
    that were used in the resolution of the case. Write everything from your perspective. Don't use your name.
    """
    sherlock_solution = openai_service.generate_sherlock_text(
        user=user, task=sherlock_prompt
    )

    inserted_id = svc.repository.add_another_part(
        user_id=jwt_data.user_id,
        story_id=input.story_id,
        content=sherlock_solution,
    )

    return CreateChatResponse(sherlock_message=str(sherlock_solution))


# conclusion
@router.post("/conclusion", status_code=200, response_model=CreateStoryResponse)
def create_conclusion(
    input: CreateStoryRequest,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    svc: Service = Depends(get_service),
):
    user = openai_service.get_user(user_id=jwt_data.user_id)
    prompt = f"""
        Write conclusion to the story. Describe how you and Sherlock, 
        after solving the case, doing mundane things. 
        Use only 3-4 sentences to end the story, don't add anything unnecessary.
            """
    response = openai_service.generate_watson_text(user=user, task=prompt)

    # generate title for a story
    title_prompt = f""" You need to create a title for a story based on its summary: {response}. 
        No more than 5 words in the title.
        Use " " for both sides of the title."""
    title = openai_service.generate_watson_text(user=user, task=title_prompt)
    svc.repository.update_title(
        title=title, user_id=jwt_data.user_id, story_id=input.story_id
    )

    inserted_id = svc.repository.add_another_part(
        user_id=jwt_data.user_id,
        story_id=input.story_id,
        content=response,
    )

    return CreateStoryResponse(
        inserted_id=input.story_id, generated_story=str(response)
    )
