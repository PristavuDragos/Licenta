import hashlib
import random
import string

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
    is_active = True
    if params[3]:  # create session for later
        is_active = False
    try:
        while meeting_session_collection.count_documents({"session_code": session_code}) != 0:
            session_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        hash_password = hashlib.sha256(bytes(session_password, "utf-8"))
        session = {
            "session_name": session_name,
            "session_code": session_code,
            "password": hash_password.hexdigest(),
            "is_active": is_active,
            "owner": session_owner
        }
        meeting_session_collection.insert_one(session)
        return session_code
    except Exception as err:
        print(str(err))
    return None


def start_session():
    pass


def check_if_active(params):
    global meeting_session_collection
    session_code = params[0]
    try:
        if meeting_session_collection.count_documents({"session_code": session_code}) != 0:
            session = meeting_session_collection.find_one({"session_code": session_code})
            return session["is_active"]
    except Exception as err:
        print(str(err))
    return False
