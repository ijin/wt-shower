from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(120), unique=True)
    credits = Column(Integer, unique=True)

    def __init__(self, name=None, email=None, password=None, credits=18):
        self.name = name
        self.email = email
        self.password = password
        self.credits = credits

    def __repr__(self):
        return '<User %r>' % (self.name)
