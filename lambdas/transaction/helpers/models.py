from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, validator
from typing import Any, Coroutine, Optional, List
from lambdas.transaction.helpers.jwt.jwt_manager import create_token, validate_token
from fastapi import FastAPI, Body, HTTPException, Path, Query, Depends, Request
import re
class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != 'admin@gmail.com':
            raise HTTPException(status_code=403, detail='Invalid Credentials')


class User(BaseModel):
    email: str
    password: str


class Movie(BaseModel):
    id: Optional[int]
    # title: str = Field(default="Movie title",min_length=5,max_length=15)
    title: str = Field(min_length=5, max_length=15)
    # overview: str = Field(default="Movie description",min_length=15,max_length=50)
    overview: str = Field(min_length=15, max_length=50)
    # year: int = Field(default=2022, le=2022)
    year: int = Field(le=2022)
    rating: float = Field(ge=1, le=10)
    category: str = Field(min_length=5, max_length=15)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Movie title",
                "overview": "Movie description",
                "year": 2022,
                "rating": 9.8,
                "category": "Acción"
            }
        }

class Transaction(BaseModel):
    Title: str = Field(min_length=5, max_length=15)
    Category: int = Field(le=1000)
    Bank: int = Field(le=1000)
    MovementType: str = Field(min_length=5, max_length=15)
    Date: str = Field(min_length=5, max_length=100)
    ownerid: int = Field(le=1000)
    Description: str = Field(min_length=5, max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "Title": "transaction",
                "Category": 1,
                "Bank": 1,
                "MovementType": 'Gasto',
                "Date": '02-10-2023',
                "ownerid": 1,
                "Description": "Description"
            }
        }
        
class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=15)
    password: str = Field(min_length=4, max_length=255)
    class Config:
        json_schema_extra = {
            "example": {
                "email": "joell@test.co",
                "password": "k2m=@[7C!sQX",
            }
        }

    @validator('email')
    def validate_email(cls, email):
        if not re.match(r'^[\w\.-]+@[\w\.-]+$', email):
            raise ValueError('Invalid email address')
        return email
    
class User(BaseModel):
    email: str = Field(min_length=5, max_length=15)
    uid: str = Field(min_length=4, max_length=255)
    class Config:
        json_schema_extra = {
            "example": {
                "email": "joel@test.co",
                "uid": "111111111111",
            }
        }