from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username:str
    email:str
    password:str
    role: Optional[str] = "user"        # default is 'user'
    admin_code: Optional[str] = None 

class perticular_user_tasks(BaseModel):
    title: str
    description : str
    status: Optional[str] = "pending" 
    assigned_to_email : str
    class Config:
        orm_mode = True  # allows compatibility with SQLAlchemy models
    