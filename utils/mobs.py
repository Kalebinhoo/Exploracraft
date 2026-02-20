from icons.emojis import EMOJIS
from icons.emojis_mobs import EMOJIS_MOBS
from utils.database import inventarios

def get_dano_mob(user_id: str, mob_name: str) -> int:
    """Retorna o dano do mob baseado na dificuldade do jogador"""
    user_id_str = str(user_id)
    dificuldade = inventarios.get(user_id_str, {}).get("dificuldade", "normal")

    dano_base = {
        "Zumbi": {"facil": 2, "normal": 3, "dificil": 4.5},
        "Esqueleto": {"facil": 1, "normal": 3, "dificil": 4},
        "Aranha": {"facil": 2, "normal": 2, "dificil": 3},
        "Creeper": {"facil": 24, "normal": 49, "dificil": 73}
    }

    if mob_name in dano_base:
        dano = dano_base[mob_name][dificuldade]
        if mob_name == "Esqueleto":
            if dificuldade == "facil":
                return 1
            elif dificuldade == "normal":
                return 3
            else:
                return 4
        return int(dano)

    return 1

mobs = {
    "Zumbi": {
        "emoji": EMOJIS_MOBS['zumbi'],
        "imagem": "https://minecraft.wiki/images/Zombie_JE1.png?c65a8",
        "descricao": "Zumbi hostil que ataca jogadores à noite.",
        "vida": 20,
        "dano": 3,
        "xp": 5,
        "drops": {
            "Carne Podre": (0, 2),
            "Ferro": (0, 1),
            "Cenoura": (0, 1),
            "Batata": (0, 1)
        },
        "raridade": "comum"
    },
    "Esqueleto": {
        "emoji": EMOJIS_MOBS['esqueleto'],
        "imagem": "https://minecraft.wiki/images/Skeleton_Aiming_JE2_BE3.png?e6e26",
        "descricao": "Esqueleto arqueiro que atira flechas.",
        "vida": 20,
        "dano": 3,
        "xp": 5,
        "drops": {
            "Ossos": (0, 2),
            "Flechas": (0, 2),
            "Arco": (0, 1),
            "Cabeça de Esqueleto": (0, 1)
        },
        "raridade": "comum"
    },
    "Aranha": {
        "emoji": EMOJIS_MOBS['aranha'],
        "imagem": "https://minecraft.wiki/images/Spider_JE5_BE4.png?b090e",
        "descricao": "Aranha venenosa que ataca jogadores.",
        "vida": 16,
        "dano": 2,
        "xp": 5,
        "drops": {
            "Fio": (0, 2),
            "Olho de Aranha": (0, 1)
        },
        "raridade": "comum"
    },
    "Creeper": {
        "emoji": EMOJIS_MOBS['creeper'],
        "imagem": "https://minecraft.wiki/images/Creeper_JE3_BE1.png?dc7b2",
        "descricao": "Creeper explosivo que se aproxima silenciosamente.",
        "vida": 20,
        "dano": 49,
        "xp": 5,
        "drops": {
            "Pólvora": (0, 2)
        },
        "raridade": "raro"
    }
}