from sqlalchemy import Column, Integer, String, Boolean, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from core.config import Base

class User(Base):
    __tablename__ = "user"
    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String)
    password: str = Column(String)