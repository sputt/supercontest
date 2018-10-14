#from supercontest.models import User
#from supercontest.utilities import session_scope
#
#
#USERS_FNAME = 'users.txt'
#
#
#def read_from_users_list():
#    with open(USERS_FNAME) as fhandle:
#        users = sorted([line.strip() for line in fhandle])
#    return users
#
#
#def instantiate_rows_for_users():
#    users = read_from_users_list()
#    user_rows = [User(name=user) for user in users]
#    return user_rows
#
#
#def commit_users():
#    with session_scope() as session:
#        user_rows = instantiate_rows_for_users()
#        session.add_all(user_rows)
