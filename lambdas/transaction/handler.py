import boto3
import json
import os
from boto3.dynamodb.conditions import Key, Attr
from fastapi import FastAPI, Body, HTTPException, Path, Query, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials
from mangum import Mangum
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Coroutine, Optional, List
from lambdas.transaction.helpers.jwt.jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer
from botocore.exceptions import ClientError
from lambdas.transaction.helpers.dbClient import tableClient
from lambdas.transaction.helpers.models import JWTBearer, User, Movie, Transaction
import decimal

STAGE = os.environ.get('STAGE')
root_path = '/' if not STAGE else f'/{STAGE}'

app = FastAPI(
    title="Sample FastAPI app",
    debug=False,
    version="1.0.0",
    root_path=root_path
)

@app.get(
    path="/",
    description="Health check",
    tags=['group-tag']
)
def get():
    return HTMLResponse('<h1>Hello world</h1>')

movies = [
    {
        'id': 1,
        'title': "Avatar",
        'overview': 'Ex',
        'year': "2009",
        "rating": 7.8,
        "category": "Acción"
    },
    {
        'id': 2,
        'title': "Avatar",
        'overview': 'Ex',
        'year': "2009",
        "rating": 7.8,
        "category": "Acción"
    },
    {
        'id': 3,
        'title': "Avatar",
        'overview': 'Ex',
        'year': "2009",
        "rating": 7.8,
        "category": "Accion"
    },
]

auth = JWTBearer()

@app.get(
    '/movies',
    tags=['movies'],
    response_model=List[Movie],
    # status_code=200,
    dependencies=[Depends(auth)]
)
def get_movies() -> List[Movie]:
    return JSONResponse(status_code=200, content=movies)


@app.post('/login', tags=['auth'])
def login(user: User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.dict())
        return JSONResponse(status_code=200, content=token)


@app.get('/movies/{id}', tags=['movies'], response_model=Movie)
def get_movie(id: int = Path(ge=1, le=2000)) -> Movie:
    print(id)
    for item in movies:
        if item['id'] == id:
            return JSONResponse(status_code=200, content=item)
    return JSONResponse(status_code=404, content=[])


@app.get('/moivies', tags=['moivies'], response_model=List[Movie])
# @app.get('/movies/', tags=['movies'])
def get_moivies_by_category(
    # def get_movies_by_category(
    category: str = Query(min_length=5, max_length=15)
) -> List[Movie]:

    print(category)
    data = [item for item in movies if item['category'] == category]
    JSONResponse(content=data)


@app.post('/movies', tags=['movies'], response_model=dict, status_code=201)
def create_movies(
    # id: int = Body(),
    # title: str = Body(),
    # overview: str = Body(),
    # year: int = Body(),
    # category: str = Body(),
    # rating: float = Body()
    movie: Movie
) -> dict:
    movies.append(movie)
    return JSONResponse(status_code=200, content={'message': 'Movie has been registered'})
#   movies.append({
#       'id': id,
#       'title': title,
#       'overview': overview,
#       'year': year,
#       'category': category,
#       'rating': rating
#   })

#   return movies


@app.put('/movies/{id}', tags=['movies'], response_model=dict)
def update_movie(
    id: int,
    # title: str = Body(),
    # overview: str = Body(),
    # year: int = Body(),
    # category: str = Body(),
    # rating: float = Body()
    movie: Movie
) -> dict:
    for item in movies:
        if item['id'] == id:
            item['title'] = movie.title
            item['overview'] = movie.overview
            item['year'] = movie.year
            item['category'] = movie.category
            item['rating'] = movie.rating
    return JSONResponse(content={'message': 'Movie has been modified'})
    # return movies


@app.delete('/movies/{id}', tags=['movies'], response_model=dict)
def delete_movie(id: int) -> dict:
    for item in movies:
        if item['id'] == id:
            movies.remove(item)
    return JSONResponse(content={'message': 'Movie has been removed'})
    # return movies

# @app.post('/transaction', tags=['transaction'])
# def create_transation(
#     transaction: Transaction
# ):
#     return tableClient.put_item(item={
#         "Title": transaction.Title,
#         "Category": transaction.Category,
#         "Bank": transaction.Bank,
#         "MovementType": transaction.MovementType,
#         "DateTransaction": transaction.Date,
#         "ownerid": transaction.ownerid,
#         "Description": transaction.description
#     })


# @app.get('/transaction/{category}', tags=['transaction'])
# def list_transation(
#     category: int = 1,
#     bank: int = 1,
#     movementType: str = 'Gasto',
#     ownerid: int = 1,
#     page: str = '1',
#     date: str = ''
# ):

#     filters = {
#         'category': category,
#         'bank': bank,
#         'movementType': movementType,
#         'ownerid': ownerid,
#         'page': page,
#         'date': date
#     }

#     return tableClient.get_item(filters)


handler = Mangum(app)
