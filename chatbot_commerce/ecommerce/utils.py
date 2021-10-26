import random
import string


def random_session_id():
    session = "".join(random.choices(string.ascii_uppercase + string.digits, k=30))
    return session


# def create_session(request):
#     session_number = request.session.get("session_number", random_session_id())
#     request.session["session_number"] = session_number
#     return session_number
