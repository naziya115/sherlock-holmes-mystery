# from .adapters.here_service import HereService
# from .adapters.s3_service import S3Service
from app.config import database
from .repository.repository import StoriesRepository
from dotenv import load_dotenv
import os

load_dotenv()


class Service:
    def __init__(
        self,
    ):
        self.repository = StoriesRepository(database)
        # self.s3_service = S3Service()
        # self.here_service = HereService(os.getenv("HERE_API_KEY"))


def get_service():
    svc = Service()
    return svc
