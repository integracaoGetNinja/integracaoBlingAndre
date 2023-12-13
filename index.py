from decouple import config
from flask import Flask, jsonify, make_response, request
import requests
import json
from pymongo import MongoClient
from decouple import config

client = MongoClient(
    f"mongodb+srv://{config('USER_DB')}:{config('PASSWD_DB')}@cluterb.ypmgnks.mongodb.net/?retryWrites=true&w=majority"
)

BASE_URL = "https://www.bling.com.br/Api/v3/"
db = client["integracaoBlingAndredb"]
col_bling = db["col_bling"]

app = Flask(__name__)


@app.route("/produtos", methods=["GET"])
def get_produtos():
    token = col_bling.find_one({"_id": 0})["token"]
    pagina = request.args.get('pagina')
    # limite = request.args.get('limite')
    indexproduto = request.args.get('indexproduto')

    url = f"https://www.bling.com.br/Api/v3/produtos?pagina={pagina}"

    headers = {
        'Authorization': f'Bearer {token}',
    }

    payload = []
    datas = requests.request("GET", url, headers=headers)

    if datas.status_code == 200:
        id_produtos = []

        lista = datas.json().get('data')[int(indexproduto): (int(indexproduto) + 5)]
        for data in lista:

            id_produtos.append(data.get('id'))

            url = f"https://www.bling.com.br/Api/v3/produtos/fornecedores?idProduto={data.get('id')}"

            custoPadrao = 0

            for custo in requests.request("GET", url, headers=headers).json().get('data'):
                if custo.get('padrao'):
                    custoPadrao = custo.get('precoCusto')

            payload.append({
                'id': data.get('id'),
                'sku': data.get('codigo'),
                'titulo': data.get('nome'),
                'preco': data.get('preco'),
                'custo': custoPadrao,
                'estoque': 0
            })

        url = "https://www.bling.com.br/Api/v3/estoques/saldos?idsProdutos%5B%5D="
        isPrimeiro = True

        for id_produto in id_produtos:
            if isPrimeiro:
                url += str(id_produto)
                isPrimeiro = False
            else:
                url += f"&idsProdutos%5B%5D={id_produto}"

        payloadComEstoque = []
        for data in requests.request("GET", url.replace("\n", ""), headers=headers).json().get('data'):
            for produto in payload:
                if produto.get('id') == data.get('produto').get('id'):
                    produto.update({'estoque': data.get('saldoFisicoTotal')})
                    payloadComEstoque.append(produto)

        return make_response(jsonify(payloadComEstoque), datas.status_code)


# def gerarOutroToken():
#     refresh_token = col_bling.find_one({"_id": 1})["refresh_token"]
#
#     data = {
#         'refresh_token': refresh_token,
#         'grant_type': 'refresh_token',
#
#     }
#
#     url = 'https://www.bling.com.br/Api/v3/oauth/token'
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Accept': '1.0',
#         'Authorization': f'Basic {config("BASIC_AUTHENTICATION")}'
#     }
#
#     response = requests.post(url, headers=headers, data=data)
#
#     print('tentando...')
#     print('response', response.status_code)
#     print('refresh_token', refresh_token)
#     if response.status_code == 200:
#         print('deu certo!')
#
#         col_bling.update_one(
#             {"_id": 0},
#             {"$set": {"token": response.json().get('access_token')}}
#         )

@app.route("/callback")
def callback():
    payload = request.args
    code = payload.get("code")

    payload = json.dumps({
        "grant_type": "authorization_code",
        "code": code
    })
    headers = {
        'Authorization': 'Basic ' + config('BASIC_AUTHENTICATION'),
        'Content-Type': 'application/json',
        'Cookie': 'PHPSESSID=f4aa8gc0a6kr70ag2qfbi8iu1k'
    }
    response = requests.request("POST", f"{BASE_URL}oauth/token", headers=headers, data=payload)

    if not col_bling.find_one({"_id": 0}):
        col_bling.insert_one(
            {
                "_id": 0,
                "token": response.json()["access_token"]
            }
        )

        col_bling.insert_one(
            {
                "_id": 1,
                "refresh_token": response.json()["refresh_token"]
            }
        )
    else:
        col_bling.update_one(
            {"_id": 0},
            {"$set": {"token": response.json()["access_token"]}}
        )

        col_bling.update_one(
            {"_id": 1},
            {"$set": {"refresh_token": response.json()["refresh_token"]}}
        )
    return jsonify(
        response.json()
    )


if __name__ == "__main__":
    app.run(debug=True)
