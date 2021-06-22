import hashlib
import random
import string
from bson.binary import Binary

meeting_session_collection = None


def init(db):
    global meeting_session_collection
    meeting_session_collection = db.meeting_sessions


def create_session(params):
    global meeting_session_collection
    session_name = params[0]
    session_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    session_password = params[1]
    session_owner = params[2]
    duration = params[3]
    upload_time = params[4]
    try:
        while meeting_session_collection.count_documents({"session_code": session_code}) != 0:
            session_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        hash_password = hashlib.sha256(bytes(session_password, "utf-8"))
        session = {
            "session_name": session_name,
            "session_code": session_code,
            "password": hash_password.hexdigest(),
            "owner": session_owner,
            "duration": duration,
            "upload_time": upload_time,
            "solutions": [],
            "test": b""
        }
        meeting_session_collection.insert_one(session)
        return session_code
    except Exception as err:
        print(str(err))
    return None


def get_session_subject(params):
    global meeting_session_collection
    session_code = params[0]
    try:
        session = meeting_session_collection.find_one({"session_code": session_code})
        if session is not None:
            return [True, session["test"]]
        else:
            return [False]
    except Exception as err:
        print(str(err))
    return [False]


def get_session_solutions(params):
    global meeting_session_collection
    session_code = params[0]
    try:
        session = meeting_session_collection.find_one({"session_code": session_code})
        if session is not None:
            return [True, session["solutions"]]
        else:
            return [False]
    except Exception as err:
        print(str(err))
    return [False]


def set_session_subject(params):
    global meeting_session_collection
    session_code = params[0]
    file = Binary(params[1])
    try:
        query = {"session_code": session_code}
        meeting_session_collection.update_one(query, {"$set": {"test": file}})
    except Exception as err:
        print(str(err))
        return False
    return True


def add_session_solution(params):
    session_code = params[0]
    file = Binary(params[1])
    username = params[2]
    try:
        query = {"session_code": session_code}
        meeting_session_collection.update_one(query, {"$push": {"solutions": [username, file]}})
    except Exception as err:
        print(str(err))
        return False
    return True


def validate_connection(params):
    global meeting_session_collection
    code = params[0]
    password = params[1]
    try:
        hash_password = hashlib.sha256(bytes(password, "utf-8"))
        session = meeting_session_collection.find_one({"session_code": code, "password": hash_password.hexdigest()})
        if session is not None:
            return [True, session["owner"]]
        else:
            return [False]
    except Exception as err:
        print(str(err))
    return [False]
