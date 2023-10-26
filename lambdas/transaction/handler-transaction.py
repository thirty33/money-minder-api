
import os
from fastapi import FastAPI, Body, HTTPException, Path, Query, Depends, Request
from lambdas.transaction.helpers.dbClient import tableClient
from lambdas.transaction.helpers.models import Transaction
from mangum import Mangum
import uuid

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
    transaction: Transaction
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
def update_movie(
    id: str,
    transaction: Transaction
):
    return tableClient.update_item(id, transaction);
    

handler = Mangum(app)