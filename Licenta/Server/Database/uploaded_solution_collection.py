from bson.binary import Binary

uploaded_solution_collection = None


def init(db):
    global uploaded_solution_collection
    uploaded_solution_collection = db.uploaded_solutions


def insert_solution(params):
    global uploaded_solution_collection
    session_code = params[0]
    username = params[1]
    try:
        entry_count = uploaded_solution_collection.count_documents({"session_code": session_code})
        entry_count += 1
        entry = {
            "session_code": session_code,
            "username": username,
            "session_entry_id": entry_count,
            "file": Binary(params[2])
        }
        result = uploaded_solution_collection.insert_one(entry)
        return result.inserted_id
    except Exception as err:
        print(str(err))
    return None


def get_solution_count_of_session(params):
    global uploaded_solution_collection
    session_code = params[0]
    try:
        return uploaded_solution_collection.count_documents({"session_code": session_code})
    except Exception as err:
        print(str(err))
    return None


def get_solution(params):
    global uploaded_solution_collection
    session_code = params[0]
    entry_id = params[1]
    try:
        entry = uploaded_solution_collection.find_one({"session_code": session_code, "session_entry_id": entry_id})
        if entry is not None:
            return [1, entry["username"], entry["file"]]
        else:
            return [-1]
    except Exception as err:
        print(str(err))
    return None
