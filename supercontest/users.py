from models import User
from backend import session_scope


USERS_FNAME = 'users.txt'


def read_from_users_list():
    with open(USERS_FNAME) as fhandle:
        users = sorted([line.strip() for line in fhandle])
    return users


def create_all_user_rows():
    users = read_from_users_list()
    user_rows = [User(name=user) for user in users]
    return user_rows


def add_all_user_rows():
    with session_scope() as session:
        user_rows = create_all_user_rows()
        for user in user_rows:
            session.add(user)
