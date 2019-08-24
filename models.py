from sqlalchemy import Column, Integer, String, Boolean, DATETIME
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True)
    password = Column(String(120), unique=True)
    credits = Column(Integer, unique=False)
    chef = Column(Boolean, default=False)

    def __init__(self, name=None, email=None, password=None, credits=18):
        self.name = name
        self.password = password
        self.credits = credits
        self.chef = chef

    def __repr__(self):
        return '<User %r>' % (self.name)

class Shower(Base):
    __tablename__ = 'showers'
    id = Column(Integer, primary_key=True)
    assigned_to = Column(String(50))
    started_at = Column(DATETIME)
    paused_at = Column(DATETIME)
    seconds_allocated = Column(Integer)

    def __init__(self, id=None, status=False, assigned_to=None, started_at=None, paused_at=None, seconds_allocated=0):
        self.id = id
        self.assigned_to = assigned_to
        self.started_at = datetime.now()
        self.paused_at = paused_at
        self.seconds_allocated = seconds_allocated

    def __repr__(self):
        return '<Shower %d>' % (self.id)
