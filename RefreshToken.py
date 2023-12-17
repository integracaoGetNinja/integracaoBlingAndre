import requests
from base64 import b64encode


# URL da requisição
url = 'https://www.bling.com.br/Api/v3/oauth/token?'

# Credenciais do client app (substitua [client_id] e [client_secret] pelos valores reais)
client_id = 'ee9ad705e01e6efc0cfa35975ff5a1e4cdfc5d28'
client_secret = '60751422b162e28358153f5c4bbbf4ef7064301e489a78523030bb1d73f2'

refresh_token = 'c0fedecc2c807816c69284db24d189a11ee06e64'

# Codifique as credenciais em base64
credentials = f"{client_id}:{client_secret}"
base64_credentials = b64encode(credentials.encode()).decode('utf-8')

# Parâmetros da requisição
data = {
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token
}

# Headers da requisição
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': '1.0',
    'Authorization': f'Basic {base64_credentials}'
}

# Faça a requisição POST
response = requests.post(url, data=data, headers=headers)

payload = response.json()

novo_refresh_token = payload.get('refresh_token')
novo_token = payload.get('access_token')

print(response.json())
# col_bling.update_one(
#     {"_id": 0},
#     {"$set": {"token": response.json()["access_token"]}}
# )


# from decouple import config
# from flask import Flask, jsonify, make_response, request
# import requests
# import json
# from pymongo import MongoClient
# from decouple import config
#
# client = MongoClient(
#     f"mongodb+srv://{config('USER_DB')}:{config('PASSWD_DB')}@cluterb.ypmgnks.mongodb.net/?retryWrites=true&w=majority"
# )
#
# BASE_URL = "https://www.bling.com.br/Api/v3/"
# db = client["integracaoBlingAbnerdb"]
# col_bling = db["col_bling"]
#
# regenerarToken(col_bling)
