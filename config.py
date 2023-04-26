import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Stargatesg-1aio!"#'
    SQLALCHEMY_BINDS = {
        'users': os.environ.get('USERS_DATABASE_URL') or 'sqlite:///users.db',
        'chatbot': os.environ.get('CHATBOT_DATABASE_URL') or 'sqlite:///chatbot.db'
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False