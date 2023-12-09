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
    else:
        col_bling.update_one(
            {"_id": 0},
            {"$set": {"token": response.json()["access_token"]}}
        )
    return jsonify(
        {
            "msg": "token gerado com sucesso!",
            "token": response.json()["access_token"]
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
