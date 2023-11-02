from jwt import encode, decode

def create_token(data: dict) -> str:

    payload_data = {
        "sub": "4242",
        "name": "Jessica Temporal",
        "nickname": "Jess"
    }

    my_secret = 'my_super_secret'
    
    token: str =  encode(payload=data, key="my_secret_key", algorithm="HS256")
    return token

def validate_token(token: str) -> str:
    data: dict = decode(token, key="my_secret_key", algorithms=['HS256'])
    return data