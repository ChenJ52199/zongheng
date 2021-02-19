from pymongo import MongoClient
from scrapy.utils.project import get_project_settings


settings = get_project_settings()
mongo_client = MongoClient(host=settings.get('MONGO_HOST'), port=settings.get('MONGO_PORT'))
