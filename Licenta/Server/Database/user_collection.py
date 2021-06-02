import hashlib

user_collection = None


def init(db):
    global user_collection
    user_collection = db.users


def create_user(params):
    global user_collection
    username = params[0]
    password = params[1]
    email = params[2]
    try:
        if user_collection.count_documents({"username": username}) == 0:
            hash_password = hashlib.sha256(bytes(password, "utf-8"))
            user = {
                "username": username,
                "password": hash_password.hexdigest(),
                "email": email
            }
            result = user_collection.insert_one(user)
            return result.inserted_id
    except Exception as err:
        print(str(err))
    return None


def check_credentials(params):
    global user_collection
    username = params[0]
    password = params[1]
    try:
        hash_password = hashlib.sha256(bytes(password, "utf-8"))
        user = user_collection.find_one({"username": username, "password": hash_password.hexdigest()})
        if user is not None:
            return user["_id"]
        else:
            return -1
    except Exception as err:
        print(str(err))
    return None
