from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


session = None


def get_db_uri():
    db_host = os.environ.get("DB_HOST")
    db_username = os.environ.get("DB_USERNAME")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME")

    return "postgresql://{username}:{password}@{host}:{port}/{db_name}".format(
        username=db_username,
        password=db_password,
        host=db_host,
        port="5432",
        db_name=db_name,
    )


def create_db_engine():
    db_uri = get_db_uri()
    return create_engine(db_uri)


def create_db_session(engine):
    global session
    if not session:
        Session = sessionmaker(bind=engine)
        session = Session()
    return session
