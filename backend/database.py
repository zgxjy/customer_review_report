from pymongo import MongoClient
from bson.objectid import ObjectId
import json

# MongoDB配置
MONGODB_CONFIG = {
    "connection_string": "mongodb://localhost:27017/",
    "database_name": "kinyo_db",
    "collections": {
        "reviews": "kinyo_new_reviews",
        "llm_results": "kinyo_llm_results",
        "data_result": "kinyo_data_result"
    }
}

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

class Database:
    client = None
    db = None

    @classmethod
    def connect_to_database(cls):
        cls.client = MongoClient(MONGODB_CONFIG["connection_string"])
        cls.db = cls.client[MONGODB_CONFIG["database_name"]]
        return cls.db

    @classmethod
    def close_database_connection(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def get_collection(cls, collection_name):
        if collection_name in MONGODB_CONFIG["collections"]:
            return cls.db[MONGODB_CONFIG["collections"][collection_name]]
        return None
