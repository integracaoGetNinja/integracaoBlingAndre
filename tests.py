import requests

response = requests.get('https://integracao-bling-andre.vercel.app/produtos?pagina=1&limite=5')

if response.status_code == 200:
    for data in response.json():
        print(data.get('custo'))
else:
    print('error')