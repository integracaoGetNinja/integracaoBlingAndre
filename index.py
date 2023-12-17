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
    else:
        gerarOutroToken()
        get_produtos()


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


@app.route("/produtos", methods=["PUT"])
def atualizarProduto():
    args = request.args
    sku = args.get('sku')
    novo_preco = args.get('novo_preco')
    novo_custo = args.get('novo_custo')
    novo_estoque = args.get('novo_estoque')

    apikey = "49be5976c509a005f6394e0f4d1785634bb7a4bdbfc14465c0412f4863438fb70453d9ab"

    url = f"https://bling.com.br/Api/v2/produto/{sku}/xml/"
    params = {"apikey": apikey}

    response = requests.get(url, params=params)

    # Verifica se a requisição foi bem-sucedida (código 200)
    if response.status_code == 200:
        # A resposta está disponível em formato JSON
        xml_string = response.text

        # Parse do XML
        root = ET.fromstring(xml_string)

        # Altere os valores conforme necessário
        if novo_preco:
            root.find(".//preco").text = novo_preco
        if novo_custo:
            root.find(".//precocusto").text = novo_custo
        if novo_estoque:
            root.find(".//estoqueatual").text = novo_estoque

        url = f"https://bling.com.br/Api/v2/produto/{sku}/json/"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "apikey": apikey,
            "xml": root,
        }

        requests.post(url, headers=headers, data=data)
        return jsonify({"msg": root})
    else:
        return jsonify({"msg": f"Erro na requisição. Código de status: {response.status_code}"})


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
