import random
from datetime import datetime, timedelta

CLIMAS = {
    "amanhecer": {
        "nome": "Amanhecer",
        "emoji": "🌅",
        "descricao_efeito": "O sol está nascendo! É um bom momento para começar suas atividades diárias.",
        "cor_embed": 0xFFA500,
        "imagem": "https://minecraft.wiki/images/6/6a/Plains.png",
        "duracao_minutos": 3,
    },
    "dia": {
        "nome": "Dia",
        "emoji": "☀️",
        "descricao_efeito": "Um dia ensolarado! Perfeito para explorar e coletar recursos.",
        "cor_embed": 0xFFD700,
        "imagem": "https://minecraft.wiki/images/6/6a/Plains.png",
        "duracao_minutos": 9,
    },
    "anoitecer": {
        "nome": "Anoitecer",
        "emoji": "🌇",
        "descricao_efeito": "O sol está se pondo. Prepare-se para a noite!",
        "cor_embed": 0xFF6347,
        "imagem": "https://minecraft.wiki/images/6/6a/Plains.png",
        "duracao_minutos": 2,
    },
    "noite": {
        "nome": "Noite",
        "emoji": "🌙",
        "descricao_efeito": "A noite chegou! Mobs hostis podem aparecer. Tenha cuidado!",
        "cor_embed": 0x191970,
        "imagem": "https://minecraft.wiki/images/6/6a/Plains.png",
        "duracao_minutos": 6,
    }
}

ORDEM_CLIMAS = ["amanhecer", "dia", "anoitecer", "noite"]

estado_clima_atual = {
    "clima_id": "amanhecer",
    "tempo_fim": datetime.now() + timedelta(minutes=3)
}

def get_clima_atual():
    """Retorna o dicionário do clima atual."""
    return CLIMAS[estado_clima_atual["clima_id"]]

def get_estado_clima():
    """Retorna o estado completo, incluindo o tempo de fim."""
    return estado_clima_atual

def verificar_e_atualizar_clima():
    """Verifica se o período atual acabou e avança para o próximo se necessário."""
    if datetime.now() >= estado_clima_atual["tempo_fim"]:
        set_novo_clima()
        return True
    return False

def set_novo_clima():
    """Avança para o próximo período do dia."""
    current_index = ORDEM_CLIMAS.index(estado_clima_atual["clima_id"])
    next_index = (current_index + 1) % len(ORDEM_CLIMAS)
    novo_clima_id = ORDEM_CLIMAS[next_index]

    clima_info = CLIMAS[novo_clima_id]
    duracao = clima_info["duracao_minutos"]
    estado_clima_atual["clima_id"] = novo_clima_id
    estado_clima_atual["tempo_fim"] = datetime.now() + timedelta(minutes=duracao)

def set_clima_especifico(clima_id: str):
    """Define um clima específico (para testes ou inicialização)."""
    clima_info = CLIMAS[clima_id]
    duracao = clima_info["duracao_minutos"]
    estado_clima_atual["clima_id"] = clima_id
    estado_clima_atual["tempo_fim"] = datetime.now() + timedelta(minutes=duracao)