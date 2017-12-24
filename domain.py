"""definitions and classes for working with db."""
# import json
from sqlalchemy import create_engine, MetaData, and_, or_, not_
from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy import Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import BOOLEAN
from sqlalchemy.orm import sessionmaker, relationship
import uuid
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

    def get_users(self):
        session = self.Session()
        users = [row for row in session.query(User)]
        session.close()
        return users

    def get_user_by_id(self, userId):
        session = self.Session()
        user = session.query(User).get(userId)
        groups = user.groups
        session.close()
        return user, groups


    def add_user(self, username, email, password):
        session = self.Session()
        salt_bytes = os.urandom(32)
        password_bytes = string_to_bytes(password)
        password_hash = hash_password(password_bytes, salt_bytes)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            salt=salt_bytes,
            pending=True
        )
        session.add(user)
        session.commit()
        session.close()

    def activate_user(self, username):
        session = self.Session()
        users = session.query(User).filter(User.username == username).all()
        if len(users) == 0:
            return False

        user = users[0]
        user.pending = False
        session.commit()
        session.close()
        return True

    def get_pending_users(self):
        session = self.Session()
        users = session.query(User).filter(User.pending).all()
        session.close()
        return users

    def get_groups(self):
        session = self.Session()
        users = session.query(Group).all()
        session.close()
        return users

    def login(self, username, password):
        session = self.Session()
        user = session.query(User).filter(User.username == username).first()

        password_hash = hash_password(string_to_bytes(password), user.salt)
        if (password_hash == user.password_hash):
            token = str(uuid.uuid4())
            self.add_token(token, user)
            return token

        session.close()
        return None

    def delete_user(self, userid):
        session = self.Session()
        user = session.query(User).get(userid)
        session.delete(user)
        session.commit()
        session.close()
        return True

    def accept_user(self, userid, groupid):
        session = self.Session()

        user = session.query(User).get(userid)
        group = session.query(Group).get(groupid)

        user.pending = False
        user.groups.append(group)

        session.commit()
        session.close()
        return True


    def get_user_for_token(self, token):
        return self.check_token(token)

    def add_token(self, token, user):
        millis = int(round(time.time()) * 1000)
        self.tokens[token] = {
            'userId': user.id,
            'exp': millis + (12 * 60 * 60 * 1000)
        }

    def check_token(self, token):
        if (token not in self.tokens):
            return None
        else:
            millis = int(round(time.time()) * 1000)
            if (self.tokens[token]['exp'] < millis):
                self.tokens.pop(token, None)
                return None

            self.tokens[token]['exp'] = millis + (12 * 60 * 60 * 1000)
            return self.tokens[token]['userId']

usergroup = Table('usergroup', Base.metadata,
      Column('userid', Integer, ForeignKey('user.id')),
      Column('groupid', String, ForeignKey('group.id'))
  )


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password_hash = Column(LargeBinary)
    salt = Column(LargeBinary)
    pending = Column(BOOLEAN)

    groups = relationship("Group", secondary=usergroup)

    def __repr__(self):
        return "{} - {}".format(self.username, self.email)


class Group(Base):
    __tablename__ = 'group'

    id = Column(String, primary_key=True)
    name = Column(String)

    users = relationship("User", secondary=usergroup)
