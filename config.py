import os


current_path = os.path.dirname(os.path.realpath(__file__))
db_path = "sqlite:///english_tutors.db"


class Config:
    DEBUG = True
    SECRET_KEY = "qt8yugfdr46e57r68t79oyuhhvgcxr7dfiykjb"
    SQLALCHEMY_DATABASE_URI = db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
