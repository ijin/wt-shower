from sqlalchemy import Column, Integer, String, Boolean, DATETIME
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(120), unique=True)
    credits = Column(Integer, unique=False)

    def __init__(self, name=None, email=None, password=None, credits=18):
        self.name = name
        self.email = email
        self.password = password
        self.credits = credits

    def __repr__(self):
        return '<User %r>' % (self.name)

class Shower(Base):
    __tablename__ = 'showers'
    id = Column(Integer, primary_key=True)
    #status = Column(Boolean, default=False)
    assigned = Column(Boolean, default=False)
    started_at = Column(DATETIME)
    paused_at = Column(DATETIME)
    seconds_allocated = Column(Integer)

    def __init__(self, id=None, status=False, assigned=False, started_at=None, paused_at=None, seconds_allocated=0):
        self.id = id
        #self.status = status
        self.assigned = assigned
        self.started_at = datetime.now()
        self.paused_at = paused_at
        self.seconds_allocated = seconds_allocated

    def __repr__(self):
        return '<Shower %d>' % (self.id)
