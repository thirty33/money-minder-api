import boto3, json, os

def authorize(event, context):
    
    body = json.dumps( { 'message' : "test "})

    response = {
        'statusCode': 200,
        'body': body
    }

    return response