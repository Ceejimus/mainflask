"""definitions and classes for working with db."""
# import json
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys

Base = declarative_base(metadata=MetaData(schema="authentication"))


class AuthDomain():
    def __init__(self, host, port, name, user, password):
        self.engine = create_engine(
            "postgresql://{}:{}@{}:{}/{}".format(
                user, password, host, port, name
            ),
            isolation_level="READ UNCOMMITTED"
        )
        self.Session = sessionmaker(bind=self.engine)

    def get_users(self):
        session = self.Session()
        users = [row for row in session.query(User)]
        session.close()
        return users

    def is_username_unique(self, username):
        users = self.get_users()
        usernames = [user.username for user in users]
        return username not in usernames

    def __del__(self):
        if (self.connection):
            self.connection.close()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password_hash = Column(String)
    salt = Column(String)

    def __repr__(self):
        return "{} - {}".format(self.username, self.email)
