import requests

url = "https://live.trading212.com/api/v0/equity/account/cash"

headers = {"Authorization": "20045125ZCfhgPuKIgHjVdJUokZSrVJNnvEaM"}

response = requests.get(url, headers=headers)

data = response.json()
print(data)
