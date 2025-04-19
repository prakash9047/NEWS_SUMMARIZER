from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    news_articles = relationship("NewsArticle", back_populates="user")

class NewsArticle(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    url = Column(String, unique=True, index=True)
    image_url = Column(String, nullable=True)
    published_at = Column(DateTime)
    source = Column(String)
    category = Column(String)
    summary = Column(Text, nullable=True)
    translated_title = Column(Text, nullable=True)
    translated_description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="news_articles")

class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    interaction_type = Column(String)  # 'view' or 'click'
    timestamp = Column(DateTime, server_default=func.now())
    
    # Additional fields for recommendation system
    user_id = Column(String, nullable=True)  # Anonymous users will have null user_id
    interaction_weight = Column(Float, default=1.0)  # Higher weight for clicks vs views 