"""definitions and classes for working with db."""
# import json
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from asyncio import Lock
import time
import hashlib
import os

Base = declarative_base(metadata=MetaData(schema="authentication"))


def bytes_to_string(data):
    return data.decode('utf-8')


def string_to_bytes(data):
    return data.encode('utf-8')


def hash_password(password_bytes, salt_bytes):
    return hashlib.pbkdf2_hmac(
        hashlib.sha256().name,
        password_bytes,
        salt_bytes,
        100000,
        None
    )


class AuthDomain():
    def __init__(self, host, port, name, user, password):
        self.engine = create_engine(
            "postgresql://{}:{}@{}:{}/{}".format(
                user, password, host, port, name
            ),
            isolation_level="READ UNCOMMITTED"
        )
        self.Session = sessionmaker(bind=self.engine)
        self.tokens = {}
        self.lock = Lock()

    def get_users(self):
        session = self.Session()
        users = [row for row in session.query(User)]
        session.close()
        return users

    def add_user(self, username, email, password):
        session = self.Session()
        salt_bytes = os.urandom(32)
        password_bytes = string_to_bytes(password)
        password_hash = hash_password(password_bytes, salt_bytes)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            salt=salt_bytes
        )
        session.add(user)
        session.commit()

    def login(self, username, password):
        session = self.Session()
        users = session.query(User).filter(User.username == username).all()
        if (len(users) == 0):
            return None
        user = users[0]
        password_hash = hash_password(string_to_bytes(password), user.salt)
        if (password_hash == user.password_hash):
            token = str(uuid.uuid4())
            self.add_token(token)
            return token

        return None

    def is_token_valid(self, token):
        return self.check_token(token)

    def add_token(self, token):
        yield from self.lock
        try:
            millis = int(round(time.time()) * 1000)
            self.tokens[token] = millis + (12 * 60 * 60 * 1000)
        finally:
            self.lock.release()

    def check_token(self, token):
        import sys
        print('CHECKTOKEN', file=sys.stderr)
        yield from self.lock
        try:
            if (token not in self.tokens):
                print('no token in tokens', file=sys.stderr)
                return False
            else:
                millis = int(round(time.time()) * 1000)
                if (self.tokens[token] > millis):
                    print('token expired', file=sys.stderr)
                    self.tokens.pop(token, None)
                    return False

                print('token valid', file=sys.stderr)
                self.tokens[token] = millis + (12 * 60 * 60 * 1000)
                return True
        finally:
            self.lock.release()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password_hash = Column(LargeBinary)
    salt = Column(LargeBinary)

    def __repr__(self):
        return "{} - {}".format(self.username, self.email)
