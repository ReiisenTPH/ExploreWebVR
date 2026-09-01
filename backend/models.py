from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    achievements = relationship("Achievement", back_populates="owner")

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Przechowywanie wyników wyliczonych przez Clojure
    total_score = Column(Float, default=0.0)
    is_speedrun = Column(Boolean, default=False)

    owner = relationship("User", back_populates="achievements")

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uix_user_achievement'),
    )