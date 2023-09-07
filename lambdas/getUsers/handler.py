import boto3, json, os
from fastapi import FastAPI
from mangum import Mangum
from starlette.middleware.cors import CORSMiddleware

# client = boto3.resource('dynamodb')

# IS_OFFLINE = os.getenv('IS_OFFLINE', False)
# if IS_OFFLINE:
#     boto3.Session(
#         aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID'],
#         aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY'],
#     )
#     client = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

# table = client.Table(os.environ['table_name'])

STAGE = os.environ.get('STAGE')
root_path = '/' if not STAGE else f'/{STAGE}'

app = FastAPI(
    title="Sample FastAPI app",
    debug=False,
    version="1.0.0",
    root_path=root_path
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get(
    path="/get-users", description="Health check"
)
def getUsers():
    return {"status": "OsdK"}


handler = Mangum(app)