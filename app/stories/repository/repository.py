from typing import Any
from datetime import datetime
from bson.objectid import ObjectId
from pymongo.database import Database


class StoriesRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_story(self, user_id: str, content: str, title: str):
        payload = {
            "content": content,
            "title": title,
            "user_id": ObjectId(user_id),
        }

        insert_result = self.database["stories"].insert_one(payload)
        return insert_result.inserted_id

    def update_title(self, user_id: str, story_id: str, title: str):
        return self.database["stories"].update_one(
            filter={"user_id": ObjectId(user_id), "_id": ObjectId(story_id)},
            update={
                "$set": {"title": title},
            },
        )

    def add_another_part(self, user_id: str, story_id: str, content: str):
        prev_story = self.database["stories"].find_one(
            {"user_id": ObjectId(user_id), "_id": ObjectId(story_id)}
        )

        if prev_story is None:
            return None

        return self.database["stories"].update_one(
            filter={"user_id": ObjectId(user_id), "_id": ObjectId(story_id)},
            update={
                "$set": {"content": prev_story["content"] + "$" + content},
            },
        )

    def get_prev_story(self, user_id: str, story_id: str):
        prev_story = self.database["stories"].find_one(
            {"user_id": ObjectId(user_id), "_id": ObjectId(story_id)}
        )
        return prev_story["content"]

    def get_stories(self, user_id: str) -> list:
        stories_response = self.database["stories"].find({"user_id": ObjectId(user_id)})
        return list(stories_response)

    def get_story(self, user_id: str, story_id: str) -> list:
        story = self.database["stories"].find_one(
            {"user_id": ObjectId(user_id), "_id": ObjectId(story_id)}
        )
        return story