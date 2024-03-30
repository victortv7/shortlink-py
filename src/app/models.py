from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class URL(Base):
    __tablename__ = 'urls'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    long_url = Column(String, nullable=False)
    access_count = Column(Integer, default=0, nullable=False)
