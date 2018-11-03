"""Configuration for the flask app.
"""
# custom
APP_NAME = 'South Bay Supercontest'
APP_ADDRESS = 'southbaysupercontest@gmail.com'

# flask
DEBUG = True

# sqlalchemy
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# flask-user
USER_APP_NAME = APP_NAME
USER_ENABLE_EMAIL = True
USER_REQUIRE_RETYPE_PASSWORD = False
USER_EMAIL_SENDER_NAME = APP_NAME
USER_EMAIL_SENDER_EMAIL = APP_ADDRESS

# flask-mail
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = APP_ADDRESS
MAIL_DEFAULT_SENDER = APP_ADDRESS
