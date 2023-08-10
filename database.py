from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:root@127.0.0.1:3306/TodoApp'

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:admin@localhost:5432/TodoApp'

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'

# connect_args = {'check_same_thread': False} it should only be used when working with sqlite3
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()