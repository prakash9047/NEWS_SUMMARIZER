from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class NewsArticleBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    source: str
    category: Optional[str] = None
    image_url: Optional[str] = None
    summary: Optional[str] = None
    translated_title: Optional[str] = None
    translated_description: Optional[str] = None

class NewsArticleCreate(NewsArticleBase):
    published_at: datetime

class NewsArticleResponse(NewsArticleBase):
    id: int
    published_at: datetime
    created_at: datetime
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

class TextInput(BaseModel):
    text: str
    max_length: Optional[int] = 150

class SummaryResponse(BaseModel):
    summary: str 