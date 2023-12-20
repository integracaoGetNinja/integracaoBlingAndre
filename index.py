from decouple import config
from flask import Flask, jsonify, make_response, request
import requests
import json
from pymongo import MongoClient
from decouple import config
from base64 import b64encode
import xml.etree.ElementTree as ET

client = MongoClient(
    f"mongodb+srv://{config('USER_DB')}:{config('PASSWD_DB')}@cluterb.ypmgnks.mongodb.net/?retryWrites=true&w=majority"
)

BASE_URL = "https://www.bling.com.br/Api/v3/"
db = client["integracaoBlingAndredb"]
col_bling = db["col_bling"]

app = Flask(__name__)


@app.route("/produto", methods=["GET"])
def get_produtos():
    token = col_bling.find_one({"_id": 0})["token"]
    sku = request.args.get('sku')

    url = f"https://www.bling.com.br/Api/v3/produtos?codigo={sku}"

    headers = {
        'Authorization': f'Bearer {token}',
    }
    try:
        data = requests.request("GET", url, headers=headers).json().get('data')

        if len(data) > 0:
            produto = data[0]

            url = f"https://www.bling.com.br/Api/v3/produtos/fornecedores?idProduto={produto.get('id')}"
            dataCusto = requests.request("GET", url, headers=headers).json().get('data')

            precoCusto = dataCusto[0].get('precoCusto')

            url = f"https://www.bling.com.br/Api/v3/estoques/saldos?idsProdutos%5B%5D={produto.get('id')}"
            dataEstoque = requests.request("GET", url, headers=headers).json().get('data')

            estoque = dataEstoque[0].get('saldoFisicoTotal')

            return jsonify({
                'id': produto.get('id'),
                'sku': produto.get('codigo'),
                'titulo': produto.get('nome'),
                'preco': produto.get('preco'),
                'custo': precoCusto,
                'estoque': estoque
            })
        else:
            jsonify({"msg": "produto não encontrado!"})
    except:
        gerarOutroToken()


def gerarOutroToken():
    url = 'https://www.bling.com.br/Api/v3/oauth/token?'

    # Credenciais do client app (substitua [client_id] e [client_secret] pelos valores reais)
    client_id = 'ee9ad705e01e6efc0cfa35975ff5a1e4cdfc5d28'
    client_secret = '60751422b162e28358153f5c4bbbf4ef7064301e489a78523030bb1d73f2'

    refresh_token = col_bling.find_one({"_id": 1})["refresh_token"]

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

    col_bling.update_one(
        {"_id": 0},
        {"$set": {"token": novo_token}}
    )

    col_bling.update_one(
        {"_id": 1},
        {"$set": {"refresh_token": novo_refresh_token}}
    )

    print('token gerado', novo_token, 'refresh', refresh_token)
    get_produtos()


@app.route("/produtos", methods=["PUT"])
def atualizarProduto():
    args = request.args
    sku = args.get('sku')
    novo_preco = args.get('novo_preco')
    novo_custo = args.get('novo_custo')
    novo_estoque = args.get('novo_estoque')

    apikey = "49be5976c509a005f6394e0f4d1785634bb7a4bdbfc14465c0412f4863438fb70453d9ab"

    url = f"https://bling.com.br/Api/v2/produto/{sku}/json/"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "apikey": apikey,
        "xml": f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <produto>
            <vlr_unit>{novo_preco}</vlr_unit>
            <preco_custo>{novo_custo}</preco_custo>
            <estoque>{novo_estoque}</estoque>
        </produto>
        """,
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 201:
        return jsonify({"msg": "ok"})
    else:
        return jsonify({"msg": response.text})


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
