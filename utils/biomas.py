from typing import Dict, Any

BIOMAS = {
    "https://minecraft.wiki/images/thumb/Cherry_Grove.png/600px-Cherry_Grove.png?fd915": {
        "nome": "Bosque de Cerejeiras",
        "madeira": "Tronco de Cerejeira",
        "emoji_madeira": "<:TroncodeCerejeira:1411227955568443423>"
    },
    "https://pt.minecraft.wiki/images/thumb/Forest.png/600px-Forest.png?cddc0": {
        "nome": "Floresta",
        "madeira": "Tronco de Carvalho",
        "emoji_madeira": "<:TroncodeCarvalho:1391156468039811132>"
    },
    "https://minecraft.wiki/images/thumb/Birch_Forest.png/600px-Birch_Forest.png?c72b9": {
        "nome": "Floresta de Bétulas",
        "madeira": "Tronco de Betula",
        "emoji_madeira": "<:TroncodeBtula:1411238279088439296>"
    },
    "https://minecraft.wiki/images/thumb/Dark_Forest.png/600px-Dark_Forest.png?f84df": {
        "nome": "Floresta Escura",
        "madeira": "Tronco de Carvalho Escuro",
        "emoji_madeira": "<:TroncodeCarvalhoEscuro:1411238273954615337>"
    },
    "https://minecraft.wiki/images/thumb/Giant_Tree_Taiga.png/600px-Giant_Tree_Taiga.png?adba8": {
        "nome": "Taiga de Árvores Gigantes",
        "madeira": "Tronco de Abeto",
        "emoji_madeira": "<:TroncodeAbeto:1411238280753582170>"
    },
    "https://minecraft.wiki/images/thumb/Jungle.png/600px-Jungle.png?f8caa": {
        "nome": "Selva",
        "madeira": "Tronco de Selva",
        "emoji_madeira": "<:TroncodeSelva:1411238277301665903>"
    },
    "https://minecraft.wiki/images/thumb/Savanna.png/600px-Savanna.png?c0845": {
        "nome": "Savana",
        "madeira": "Tronco de Acacia",
        "emoji_madeira": "<:TroncodeAcrcia:1411238275410296905>"
    },
    "https://minecraft.wiki/images/Mangrove_Swamp.png?49200": {
        "nome": "Pântano de Mangue",
        "madeira": "Tronco de Mangue",
        "emoji_madeira": "<:TroncodeMangue:1418841639056707665>"
    },
}

def get_bioma_info(bioma_url: str) -> Dict[str, Any]:
    """Retorna as informações do bioma com base na URL."""
    return BIOMAS.get(bioma_url, {
        "nome": "Planície",
        "madeira": "Tronco de Carvalho",
        "emoji_madeira": "<:TroncodeCarvalho:1391156468039811132>"
    })

def get_madeira_do_bioma(bioma_url: str) -> str:
    """Retorna o tipo de madeira específica do bioma."""
    return get_bioma_info(bioma_url)["madeira"]

def get_emoji_madeira(bioma_url: str) -> str:
    """Retorna o emoji da madeira específica do bioma."""
    return get_bioma_info(bioma_url)["emoji_madeira"]

def get_nome_bioma(bioma_url: str) -> str:
    """Retorna o nome do bioma."""
    return get_bioma_info(bioma_url)["nome"]
