import json
import os

PASTA_SAVES = "saves"

if not os.path.exists(PASTA_SAVES):
    os.mkdir(PASTA_SAVES)

def salvar_mundo(user_id: str, slot: str, bioma: str):
    caminho = os.path.join(PASTA_SAVES, f"{user_id}.json")

    dados = {}
    if os.path.exists(caminho):
        try:
            with open(caminho, "r") as f:
                dados = json.load(f)
        except json.JSONDecodeError:
            dados = {}

    dados[slot] = {"bioma": bioma}

    with open(caminho, "w") as f:
        json.dump(dados, f, indent=4)

def carregar_mundo(user_id: str, slot: str):
    caminho = os.path.join(PASTA_SAVES, f"{user_id}.json")

    if not os.path.exists(caminho):
        return None

    try:
        with open(caminho, "r") as f:
            dados = json.load(f)
    except json.JSONDecodeError:
        return None

    return dados.get(slot)
