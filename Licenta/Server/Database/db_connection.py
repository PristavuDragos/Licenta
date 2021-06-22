from pymongo import MongoClient
from Server.Database import meeting_session_collection
from Server.Database import user_collection
from Server.Database import uploaded_solution_collection

client = None
db = None


def init(settings):
    global client
    global db
    client = MongoClient(settings["db_connection_string"])
    db = client["licenta"]
    meeting_session_collection.init(db)
    user_collection.init(db)
    uploaded_solution_collection.init(db)


