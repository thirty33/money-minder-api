
import os
from fastapi import FastAPI, Body, HTTPException, Path, Query, Depends, Request, security, status
from lambdas.transaction.helpers.dbClient import tableClient
from lambdas.transaction.authClient import authClient, get_current_user
from lambdas.transaction.helpers.models import Transaction, LoginRequest, User
from mangum import Mangum
import uuid
import json


STAGE = os.environ.get('STAGE')
root_path = '/' if not STAGE else f'/{STAGE}'


app = FastAPI(
    title="Money Minder Api",
    debug=False,
    version="1.0.0",
    root_path=root_path
)

@app.post('/transaction', tags=['transaction'])
def create_transation(
    transaction: Transaction,
    sub: str = Depends(get_current_user),
    token: str = ''
):
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
    date: str = '',
    sub: str = Depends(get_current_user),
    token: str = ''
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
def delete_transaction(id: str, sub: str = Depends(get_current_user), token: str = ''):
    return tableClient.delete_item(id)

@app.put('/transaction/{id}', tags=['transaction'], response_model=dict)
def update_transaction(
    id: str,
    transaction: Transaction, 
    sub: str = Depends(get_current_user),
    token: str = ''
):
    return tableClient.update_item(id, transaction);


@app.post('/user/create', tags=['user'])
def create_user(
    login_request: LoginRequest,
):
    tableCLientResponse = {}
    data_dict = {}
    createUserResponse = authClient.admin_create_user(login_request.email, login_request.password)
    
    if createUserResponse['status_code'] and createUserResponse['status_code'] >= 200 and createUserResponse['status_code'] < 204:
        tableClient.set_table(os.environ.get('user_transaction_name'))
        tableCLientResponse = tableClient.put_item(item={
            "Email": login_request.email,
            "Password": login_request.password,
            "Uid": str(uuid.uuid4())
        })
        json_content = tableCLientResponse.body.decode()
        data_dict = json.loads(json_content)

    data = {
        'create-user-cognito': json.loads(json.dumps(createUserResponse, default=authClient.serialize_datetime)),
        'create-user-dynamo': data_dict
    }
    return tableClient.manage_sucessfull_response(data, 201)

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