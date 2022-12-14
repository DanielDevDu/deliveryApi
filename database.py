from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker

import environ

# variables from environment
env = environ.Env(DEBUG=(bool, False))

# Read router.env file
environ.Env.read_env(".env")

USER = env("POSTGRES_USER")
PASSWORD = env("POSTGRES_PASSWORD")
HOST = env("POSTGRES_HOST")
PORT = env("POSTGRES_PORT")
DATABASE = env("POSTGRES_DB")

engine=create_engine('postgresql://{0}:{1}@{2}:{3}/{4}'.format(
    USER,
    PASSWORD,
    HOST,
    str(PORT),
    DATABASE
),
    echo=True
)

Base=declarative_base()

Session=sessionmaker()