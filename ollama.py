import requests

models = requests.get("http://localhost:11434/v1/models").json()

#print(models)

for model in models.get("data"):
    print(model.get("id"))