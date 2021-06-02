from pymongo import MongoClient
import meeting_session_collection
import user_collection

client = None
db = None


def init():
    global client
    global db
    client = MongoClient("mongodb://localhost:27017")
    db = client["licenta"]
    meeting_session_collection.init(db)
    user_collection.init(db)





if __name__ == '__main__':
    init()
    # tutorial1 = {
    #     "title": "Working With JSON Data in Python",
    #     "author": "Lucas",
    #     "contributors": [
    #         "Aldren",
    #         "Dan",
    #         "Joanna"],
    #     "url": "https://realpython.com/python-json/"
    # }
    testing_collection = db.testing
    string0 = "title"
    string1 = "Working With JSON Data in Python"
    # result = testing_collection.insert_one(tutorial1)
    doc = testing_collection.find_one({"author": "Lucas", "title": "Working With JSON Data in Python"})
    if doc is not None:
        print(doc["_id"])
    # print(f"One tutorial: {result.inserted_id}")
    # client.close()
    # user_collection.create_user(["test1", "test1"])

