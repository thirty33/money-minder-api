
import boto3
import json
from botocore.exceptions import ClientError
import decimal
import os
from fastapi.responses import HTMLResponse, JSONResponse
from boto3.dynamodb.conditions import Attr
from fastapi import Depends, HTTPException, Request, status
import random
import string
import jwt
from jwt import PyJWKClient
import httpx

class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class AuthClient(metaclass=SingletonMeta):

    def instance(self):
        self.client = boto3.client('cognito-idp', region_name=os.getenv('AWS_REGION', False))
        self.user_pool_id = os.getenv('user_pool_id', False)
        self.client_id = os.getenv('client_id', False)

    def manage_sucessfull_response(self, response, status_code=201):
        return {
            'content': {
                'error': 'false',
                'data': response
            },
            'status_code': status_code
        }

    def manage_failed_response(self, err):
        return {
            'content': {
                'error': 'true',
                'response': err.response['Error']['Message'],
            },
            'status_code': 401
        }
    
    def admin_create_user(self, username, temporary_password):
        try: 
            # print('self.user_pool_id', self.user_pool_id)
            response = self.client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=username,
                TemporaryPassword=temporary_password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': username
                    },
                    {
                        'Name': 'email_verified',
                        'Value': 'true'
                    }
                ],
                MessageAction='SUPPRESS',
                # ForceAliasCreation=False,
            )
            # print('response', response)

            user = response.get('User', '')
            # print('user', user)
            set_password_response = {};
            if user:
                set_password_response = self.admin_set_user_password(username, temporary_password)

            response['setPasswordResponse'] = set_password_response;
            return self.manage_sucessfull_response(response)
        
        except ClientError as err:
            # print('error', err.response['Error']['Message'])
            return self.manage_failed_response(err)
        
    def generate_password(self, length=12, complexity='medium'):
        characters = string.ascii_letters + string.digits

        if complexity == 'medium':
            characters += string.punctuation

        password = ''.join(random.choice(characters) for _ in range(length))
        return password

    def admin_set_user_password(self, username, password):

        # generated_password = self.generate_password(length=12, complexity='medium')
        generated_password = password
        
        try:
            response = self.client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=username,
                Password=generated_password,
                Permanent=True
            )
            return response
            # print('response admin_set_user_password', response)
        except ClientError as err:
            return self.manage_failed_response(err)

    def admin_initiate_auth(self, username, password):
        try:
            response = self.client.admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            return response
        except ClientError as err:
            raise err
    

authClient = AuthClient()
authClient.instance()

COGNITO_REGION = os.environ.get("AWS_REGION")
COGNITO_USER_POOL_ID =  os.environ.get("user_pool_id")

async def get_cognito_jwt_secret() -> str:
    JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

    async with httpx.AsyncClient() as client:
        response = await client.get(JWKS_URL)

    if response.status_code != 200:
        raise Exception("Failed to fetch JWKS from Cognito")
    
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

# Cognito jwt auth validation
async def get_current_user(token: str = Depends(get_token)) -> str:
    JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    
    client = PyJWKClient(JWKS_URL)
    
    try:
        header = jwt.get_unverified_header(token)
        key = client.get_signing_key(header["kid"])
        public_key = key.key
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        
