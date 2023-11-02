
import os
from fastapi import FastAPI, Body, HTTPException, Path, Query, Depends, Request, security, status
from lambdas.transaction.helpers.dbClient import tableClient
from lambdas.transaction.authClient import authClient
from lambdas.transaction.helpers.models import Transaction, LoginRequest, User
from mangum import Mangum
import uuid

import jwt
from jwt import PyJWKClient
import httpx


STAGE = os.environ.get('STAGE')
root_path = '/' if not STAGE else f'/{STAGE}'

COGNITO_DOMAIN = os.environ.get("COGNITO_DOMAIN")
COGNITO_CLIENT_ID = os.environ.get("client_id")
COGNITO_CLIENT_SECRET = os.environ.get("COGNITO_CLIENT_SECRET")
COGNITO_REDIRECT_URI = os.environ.get("COGNITO_REDIRECT_URI")
COGNITO_REGION = os.environ.get("AWS_REGION")
COGNITO_USER_POOL_ID =  os.environ.get("user_pool_id")

AUTH_URL = f"https://{COGNITO_DOMAIN}/oauth2/authorize"
TOKEN_URL = f"https://{COGNITO_DOMAIN}/oauth2/token"
LOGOUT_URL = f"https://{COGNITO_DOMAIN}/logout"

async def get_cognito_jwt_secret() -> str:
    JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

    async with httpx.AsyncClient() as client:
        response = await client.get(JWKS_URL)

    if response.status_code != 200:
        raise Exception("Failed to fetch JWKS from Cognito")

    print('this is response', response)

    jwks = response.json()
    for key_data in jwks["keys"]:
        if key_data["alg"] == "RS256" and key_data["use"] == "sig":
            key = jwk.construct(key_data)
            return key.to_pem().decode("utf-8")

    raise Exception("Failed to find a suitable public key in JWKS")


        
        
async def get_token(request: Request):
    token = request.query_params.get("token")
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is required")
    return token

async def get_current_user(token: str = Depends(get_token)) -> str:
    JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

    print('JWKS_URL', JWKS_URL)
    
    client = PyJWKClient(JWKS_URL)
    print('client', client)

    try:
        header = jwt.get_unverified_header(token)
        print('kid',header["kid"])
        key = client.get_signing_key(header["kid"])
        print('key', key)
        public_key = key.key
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        print('payload',payload)
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    # except jwt.JWTClaimsError:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims")
    # except jwt.JWTError:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
        


app = FastAPI(
    title="Money Minder Api",
    debug=False,
    version="1.0.0",
    root_path=root_path
)

@app.post('/transaction', tags=['transaction'])
def create_transation(
    transaction: Transaction,
    sub: str = Depends(get_current_user)
):
    
    # print('type', type(uuid.uuid4()))
    return tableClient.put_item(item={
        "Title": transaction.Title,
        "Category": transaction.Category,
        "Bank": transaction.Bank,
        "MovementType": transaction.MovementType,
        "DateTransaction": transaction.Date,
        "ownerid": transaction.ownerid,
        "Description": transaction.Description,
        "Uid": str(uuid.uuid4())
    })


@app.get('/transaction/{category}', tags=['transaction'])
def list_transation(
    category: int = 1,
    bank: int = 1,
    movementType: str = 'Gasto',
    ownerid: int = 1,
    page: str = '1',
    date: str = ''
):

    filters = {
        'category': category,
        'bank': bank,
        'movementType': movementType,
        'ownerid': ownerid,
        'page': page,
        'date': date
    }

    return tableClient.get_item(filters)

@app.delete('/transaction/{id}', tags=['transaction'])
def delete_transaction(id: str):
    return tableClient.delete_item(id)

@app.put('/transaction/{id}', tags=['transaction'], response_model=dict)
def update_transaction(
    id: str,
    transaction: Transaction
):
    return tableClient.update_item(id, transaction);


@app.post('/user/create', tags=['user'])
def create_user(
    login_request: LoginRequest
):
    return authClient.admin_create_user(login_request.email, login_request.password)
    # return authClient.admin_initiate_auth(login_request.email, login_request.password)
    # return authClient.admin_create_user(login_request.email, login_request.password)
    # print('test', os.environ.get('user_transaction_name'))
    # tableClient.set_table(os.environ.get('user_transaction_name'))
    # return tableClient.put_item(item={
    #     "Email": login_request.email,
    #     "Password": login_request.password,
    #     "Uid": str(uuid.uuid4())
    # })

@app.get('/user/login', tags=['user'])
def login_user(
    login_request: LoginRequest = Depends()
):
    response = authClient.admin_initiate_auth(login_request.email, login_request.password)
    return tableClient.manage_sucessfull_response(response)
    # print('test', os.environ.get('user_transaction_name'))
    # tableClient.set_table(os.environ.get('user_transaction_name'))

    # return tableClient.get_single_model({
    #     "Email": email,
    #     "Uid": uid
    # })
    

handler = Mangum(app)