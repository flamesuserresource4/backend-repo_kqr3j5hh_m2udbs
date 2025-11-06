"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each model name lowercased becomes the collection name (e.g., Project -> "project").
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# --------------------
# Portfolio Schemas
# --------------------

class Contact(BaseModel):
    """Contact messages collection schema -> collection: "contact"""
    name: str = Field(..., min_length=1, max_length=120, description="Sender full name")
    email: EmailStr = Field(..., description="Valid email address")
    message: str = Field(..., min_length=1, max_length=2000, description="Message body")


class Project(BaseModel):
    """Projects collection schema -> collection: "project"""
    title: str = Field(..., min_length=1, max_length=160)
    description: Optional[str] = Field(None, max_length=1000)
    image_url: Optional[str] = Field(None, description="Public image URL")
    link: Optional[str] = Field(None, description="External link to project")


# Example schemas kept for reference (not used by portfolio API)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
