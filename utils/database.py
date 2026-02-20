def adicionar_item_sqlite(jogador_id, item, quantidade=1):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO inventario (jogador_id, item, quantidade)
                     VALUES (?, ?, ?)
                     ON CONFLICT(jogador_id, item) DO UPDATE SET quantidade = quantidade + ?''',
                  (jogador_id, item, quantidade, quantidade))
        conn.commit()

def remover_item_sqlite(jogador_id, item, quantidade=1):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('SELECT quantidade FROM inventario WHERE jogador_id = ? AND item = ?', (jogador_id, item))
        row = c.fetchone()
        if row and row[0] >= quantidade:
            nova_qtd = row[0] - quantidade
            if nova_qtd > 0:
                c.execute('UPDATE inventario SET quantidade = ? WHERE jogador_id = ? AND item = ?', (nova_qtd, jogador_id, item))
            else:
                c.execute('DELETE FROM inventario WHERE jogador_id = ? AND item = ?', (jogador_id, item))
            conn.commit()
            return True
        return False

def get_inventario_sqlite(jogador_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('SELECT item, quantidade FROM inventario WHERE jogador_id = ?', (jogador_id,))
        return dict(c.fetchall())

def adicionar_xp_sqlite(jogador_id, quantidade_xp):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('SELECT xp FROM jogadores WHERE id = ?', (jogador_id,))
        row = c.fetchone()
        xp_atual = row[0] if row else 0
        novo_xp = xp_atual + quantidade_xp
        c.execute('UPDATE jogadores SET xp = ? WHERE id = ?', (novo_xp, jogador_id))
        conn.commit()
        return novo_xp

def get_xp_sqlite(jogador_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('SELECT xp FROM jogadores WHERE id = ?', (jogador_id,))
        row = c.fetchone()
        return row[0] if row else 0

def adicionar_missao_sqlite(jogador_id, missao, status, recompensa):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO missoes (jogador_id, missao, status, recompensa) VALUES (?, ?, ?, ?)',
                  (jogador_id, missao, status, recompensa))
        conn.commit()

def get_missoes_sqlite(jogador_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('SELECT missao, status, recompensa FROM missoes WHERE jogador_id = ?', (jogador_id,))
        return c.fetchall()
import sqlite3
from contextlib import closing

DB_PATH = 'minecraft.db'

def get_difficulty_multiplier(dificuldade, type_multiplier):
    """Retorna o multiplicador baseado na dificuldade."""
    if dificuldade == "facil":
        return 1.5 if type_multiplier == "reward" else 0.5
    elif dificuldade == "dificil":
        return 0.5 if type_multiplier == "reward" else 1.5
    else:
        return 1.0

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS jogadores (
            id TEXT PRIMARY KEY,
            nome TEXT,
            moedas INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            nivel INTEGER DEFAULT 1,
            notificacoes INTEGER DEFAULT 1,
            registered INTEGER DEFAULT 0,
            vida INTEGER DEFAULT 10,
            fome INTEGER DEFAULT 10,
            bioma_atual TEXT
        )''')
        try:
            c.execute('ALTER TABLE jogadores ADD COLUMN blocos_quebrados INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass
        c.execute('''CREATE TABLE IF NOT EXISTS inventario (
            jogador_id TEXT,
            item TEXT,
            quantidade INTEGER,
            PRIMARY KEY (jogador_id, item)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS missoes (
            jogador_id TEXT,
            missao TEXT,
            status TEXT,
            recompensa TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS cooldowns (
            jogador_id TEXT,
            comando TEXT,
            timestamp INTEGER
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS ranking (
            jogador_id TEXT,
            tipo TEXT,
            valor INTEGER
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS clans (
            nome TEXT PRIMARY KEY,
            dono TEXT,
            membros TEXT,
            conquistas TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS logs (
            jogador_id TEXT,
            acao TEXT,
            detalhes TEXT,
            timestamp INTEGER
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS historico_comandos (
            jogador_id TEXT,
            comando TEXT,
            timestamp INTEGER
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS maintenance (
            command TEXT PRIMARY KEY,
            active INTEGER DEFAULT 0
        )''')
        conn.commit()

def adicionar_moedas(jogador_id, valor):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO jogadores (id, moedas) VALUES (?, ?) ON CONFLICT(id) DO UPDATE SET moedas = moedas + ?', (jogador_id, valor, valor))
        conn.commit()

def get_moedas(jogador_id):
    """Retorna o saldo de moedas do jogador."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('SELECT moedas FROM jogadores WHERE id = ?', (jogador_id,))
        row = c.fetchone()
        return row[0] if row else 0

def adicionar_blocos_quebrados(jogador_id, quantidade):
    """Adiciona blocos quebrados ao jogador."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('UPDATE jogadores SET blocos_quebrados = blocos_quebrados + ? WHERE id = ?', (quantidade, jogador_id))
        conn.commit()

def get_blocos_quebrados(jogador_id):
    """Retorna o total de blocos quebrados do jogador."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('SELECT blocos_quebrados FROM jogadores WHERE id = ?', (jogador_id,))
        row = c.fetchone()
        return row[0] if row else 0

import json
import os

ARQUIVO_INVENTARIO = "inventarios.json"
ARQUIVO_TENTATIVAS = "tentativas_cacar.json"
ARQUIVO_COLETANDO = "usuarios_coletando.json"
ARQUIVO_VEZES_EXPLORAR = "vezes_explorar.json"
ARQUIVO_TRAVEL_STATE = "travel_state.json"

if os.path.exists(ARQUIVO_INVENTARIO):
    try:
        with open(ARQUIVO_INVENTARIO, "r") as f:
            inventarios = json.load(f)
    except json.JSONDecodeError:
        inventarios = {}
else:
    inventarios = {}

if os.path.exists(ARQUIVO_TENTATIVAS):
    try:
        with open(ARQUIVO_TENTATIVAS, "r") as f:
            tentativas_cacar = json.load(f)
    except json.JSONDecodeError:
        tentativas_cacar = {}
else:
    tentativas_cacar = {}

if os.path.exists(ARQUIVO_COLETANDO):
    try:
        with open(ARQUIVO_COLETANDO, "r") as f:
            usuarios_coletando_list = json.load(f)
            usuarios_coletando = set(usuarios_coletando_list)
    except json.JSONDecodeError:
        usuarios_coletando = set()
else:
    usuarios_coletando = set()

if os.path.exists(ARQUIVO_VEZES_EXPLORAR):
    try:
        with open(ARQUIVO_VEZES_EXPLORAR, "r") as f:
            vezes_explorar = json.load(f)
    except json.JSONDecodeError:
        vezes_explorar = {}
else:
    vezes_explorar = {}

if os.path.exists(ARQUIVO_TRAVEL_STATE):
    try:
        with open(ARQUIVO_TRAVEL_STATE, "r") as f:
            travel_state = json.load(f)
    except json.JSONDecodeError:
        travel_state = {}
else:
    travel_state = {}

mensagens_coleta = {}

def salvar_inventarios():
    with open(ARQUIVO_INVENTARIO, "w") as f:
        json.dump(inventarios, f, indent=4)

def salvar_tentativas_cacar():
    with open(ARQUIVO_TENTATIVAS, "w") as f:
        json.dump(tentativas_cacar, f, indent=4)

def salvar_usuarios_coletando():
    with open(ARQUIVO_COLETANDO, "w") as f:
        json.dump(list(usuarios_coletando), f, indent=4)

def salvar_vezes_explorar():
    with open(ARQUIVO_VEZES_EXPLORAR, "w") as f:
        json.dump(vezes_explorar, f, indent=4)

def salvar_travel_state():
    with open(ARQUIVO_TRAVEL_STATE, "w") as f:
        json.dump(travel_state, f, indent=4)

def possui_item(user_id, item):
    """Verifica se o usuário possui o item no inventário."""
    user_id = str(user_id)
    inventario = inventarios.get(user_id, {})

    def get_total(item_name):
        stacks = inventario.get(item_name, [])
        if isinstance(stacks, list):
            return sum(stacks)
        else:
            return stacks if stacks > 0 else 0

    if item == "picareta":
        return any(qtd > 0 for nome, qtd in inventario.items() if "picareta" in nome.lower())
    if item.lower().startswith("espada") or item == "🗡️ Espada":
        return any(qtd > 0 for nome, qtd in inventario.items() if "espada" in nome.lower())
    if item == "machado":
        return any(qtd > 0 for nome, qtd in inventario.items() if "machado" in nome.lower())
    if item == "enxada":
        return any(qtd > 0 for nome, qtd in inventario.items() if "enxada" in nome.lower())
    if item == "pa" or item == "pá":
        return any(qtd > 0 for nome, qtd in inventario.items() if "pa" in nome.lower() or "pá" in nome.lower())
    return get_total(item) > 0

def adicionar_item(user_id, item, quantidade=1):
    """Adiciona item ao inventário do usuário, criando stacks de 64 itens."""
    user_id = str(user_id)

    if user_id not in inventarios:
        inventarios[user_id] = {"dificuldade": "facil"}

    user_data = inventarios[user_id]
    dificuldade = user_data.get("dificuldade", "normal")

    quantidade = int(quantidade * get_difficulty_multiplier(dificuldade, "reward"))

    stacks = user_data.get(item, [])
    if not isinstance(stacks, list):
        stacks = [stacks] if stacks > 0 else []

    remaining = quantidade
    for i in range(len(stacks)):
        if stacks[i] < 64:
            can_add = min(remaining, 64 - stacks[i])
            stacks[i] += can_add
            remaining -= can_add
            if remaining <= 0:
                break

    while remaining > 0:
        can_add = min(remaining, 64)
        stacks.append(can_add)
        remaining -= can_add

    if stacks:
        user_data[item] = stacks
    else:
        if item in user_data:
            del user_data[item]

    salvar_inventarios()

    return quantidade - remaining

def remover_item(user_id, item, quantidade=1):
    """Remove item do inventário do usuário, se possível."""
    user_id = str(user_id)
    if user_id not in inventarios:
        return False
    inventario = inventarios[user_id]

    if item == "picareta":
        picaretas_disponiveis = [nome for nome, qtd in inventario.items() if "picareta" in nome.lower() and (isinstance(qtd, list) and sum(qtd) > 0 or isinstance(qtd, (int, float)) and qtd > 0)]
        quality_order = ["diamante", "ferro", "ouro", "pedra", "madeira"]
        picaretas_disponiveis.sort(key=lambda x: next((i for i, q in enumerate(quality_order) if q in x.lower()), len(quality_order)), reverse=True)

        for picareta in picaretas_disponiveis:
            stacks = inventario.get(picareta, [])
            if not isinstance(stacks, list):
                stacks = [stacks] if stacks > 0 else []
            total = sum(stacks)
            if total >= quantidade:
                remaining = quantidade
                for i in range(len(stacks) - 1, -1, -1):
                    if stacks[i] >= remaining:
                        stacks[i] -= remaining
                        remaining = 0
                        break
                    else:
                        remaining -= stacks[i]
                        stacks[i] = 0
                stacks = [s for s in stacks if s > 0]
                if stacks:
                    inventario[picareta] = stacks
                else:
                    if picareta in inventario:
                        del inventario[picareta]
                salvar_inventarios()
                return True
        return False

    stacks = inventario.get(item, [])
    if not isinstance(stacks, list):
        stacks = [stacks] if stacks > 0 else []
    total = sum(stacks)
    if total >= quantidade:
        remaining = quantidade
        for i in range(len(stacks) - 1, -1, -1):
            if stacks[i] >= remaining:
                stacks[i] -= remaining
                remaining = 0
                break
            else:
                remaining -= stacks[i]
                stacks[i] = 0
        stacks = [s for s in stacks if s > 0]
        if stacks:
            inventario[item] = stacks
        else:
            if item in inventario:
                del inventario[item]
        salvar_inventarios()
        return True
    return False

def get_inventario(user_id):
    """Retorna o inventário do usuário como dicionário."""
    user_id = str(user_id)
    return inventarios.get(user_id, {})

def alterar_item(user_id, item, quantidade):
    """Altera a quantidade de um item (pode somar ou subtrair)."""
    user_id = str(user_id)
    if user_id not in inventarios:
        inventarios[user_id] = {}
    inventario = inventarios[user_id]

    nova_quantidade = inventario.get(item, 0) + quantidade

    if nova_quantidade <= 0:
        if item in inventario:
            del inventario[item]
    else:
        inventario[item] = nova_quantidade
    salvar_inventarios()

def carregar_dados(user_id):
    """Carrega os dados de um usuário do arquivo de inventários."""
    user_id = str(user_id)
    return inventarios.get(user_id, {})

def salvar_dados(user_id, dados_usuario):
    """Salva os dados de um usuário no arquivo de inventários."""
    user_id = str(user_id)
    inventarios[user_id] = dados_usuario
    salvar_inventarios()

def verificar_materiais_construcao(user_id, materiais_necessarios):
    """Verifica se o usuário possui todos os materiais necessários para uma construção."""
    inventario = get_inventario(user_id)
    materiais_faltando = {}
    
    for material, quantidade_necessaria in materiais_necessarios.items():
        quantidade_possui = inventario.get(material, 0)
        if quantidade_possui < quantidade_necessaria:
            materiais_faltando[material] = quantidade_necessaria - quantidade_possui
    
    return len(materiais_faltando) == 0, materiais_faltando

def consumir_materiais_construcao(user_id, materiais_necessarios):
    """Consome os materiais necessários para uma construção."""
    user_id = str(user_id)
    
    pode_construir, _ = verificar_materiais_construcao(user_id, materiais_necessarios)
    if not pode_construir:
        return False
    
    for material, quantidade in materiais_necessarios.items():
        if not remover_item(user_id, material, quantidade):
            return False
    
    return True

def adicionar_construcao(user_id, nome_construcao):
    """Adiciona uma construção concluída ao inventário do usuário."""
    adicionar_item(user_id, f"🏗️ {nome_construcao}", 1)

def get_construcoes_usuario(user_id):
    """Retorna todas as construções que o usuário possui."""
    inventario = get_inventario(user_id)
    construcoes = {}
    
    for item, quantidade in inventario.items():
        if item.startswith("🏗️ "):
            nome_construcao = item.replace("🏗️ ", "")
            construcoes[nome_construcao] = quantidade
    
    return construcoes

def inicializar_usuario(user_id):
    """Inicializa um novo usuário com dados padrão."""
    user_id = str(user_id)
    if user_id not in inventarios:
        inventarios[user_id] = {
            "inventario": {},
            "xp": 0,
            "nivel": 1,
            "construcoes": {}
        }
        salvar_inventarios()
    return inventarios[user_id]

XP_TABLE = {
    1: 7, 2: 16, 3: 27, 4: 40, 5: 55, 6: 72, 7: 91, 8: 112, 9: 135, 10: 165,
    11: 187, 12: 216, 13: 247, 14: 280, 15: 315, 16: 352, 17: 394, 18: 441, 19: 493, 20: 550,
    21: 612, 22: 679, 23: 751, 24: 828, 25: 910, 26: 997, 27: 1089, 28: 1186, 29: 1288, 30: 1395,
    31: 1507, 32: 1628, 33: 1758, 34: 1897, 35: 2045, 36: 2202, 37: 2368, 38: 2543, 39: 2727, 40: 2920
}

def calcular_nivel_por_xp(xp_total):
    """Calcula o nível baseado no XP total usando a tabela do Minecraft."""
    nivel = 1
    for lvl, xp_necessario in XP_TABLE.items():
        if xp_total >= xp_necessario:
            nivel = lvl + 1
        else:
            break
    return nivel

def get_xp_para_proximo_nivel(nivel_atual):
    """Retorna quanto XP é necessário para o próximo nível."""
    xp_atual = XP_TABLE.get(nivel_atual, 0)
    xp_proximo = XP_TABLE.get(nivel_atual + 1, 999999)
    return xp_proximo - xp_atual

def get_xp_progresso_atual(xp_total, nivel_atual):
    """Calcula o progresso atual de XP para o próximo nível."""
    xp_base = XP_TABLE.get(nivel_atual, 0)
    xp_necessario = XP_TABLE.get(nivel_atual + 1, 999999)
    xp_progresso = xp_total - xp_base
    xp_faltando = xp_necessario - xp_total

    return {
        "progresso": max(0, xp_progresso),
        "necessario": xp_necessario - xp_base,
        "faltando": max(0, xp_faltando)
    }

def adicionar_xp(user_id, quantidade_xp):
    """Adiciona XP ao jogador e calcula automaticamente o nível."""
    user_id = str(user_id)

    if user_id not in inventarios:
        inventarios[user_id] = {"xp": 0, "nivel": 1, "vida": 10, "fome": 10, "registrado": 0, "dificuldade": "facil"}

    user_data = inventarios[user_id]
    dificuldade = user_data.get("dificuldade", "normal")

    quantidade_xp = int(quantidade_xp * get_difficulty_multiplier(dificuldade, "reward"))

    xp_antigo = user_data.get("xp", 0)
    nivel_antigo = user_data.get("nivel", 1)

    novo_xp = xp_antigo + quantidade_xp
    novo_nivel = calcular_nivel_por_xp(novo_xp)

    user_data["xp"] = novo_xp
    user_data["nivel"] = novo_nivel
    salvar_inventarios()

    subiu_nivel = novo_nivel > nivel_antigo
    return {
        "xp_ganho": quantidade_xp,
        "xp_total": novo_xp,
        "nivel_atual": novo_nivel,
        "subiu_nivel": subiu_nivel,
        "nivel_anterior": nivel_antigo
    }

def alterar_vida(user_id, quantidade):
    """Altera a vida do jogador (positivo para curar, negativo para dano)."""
    user_id = str(user_id)

    if user_id not in inventarios:
        inventarios[user_id] = {"xp": 0, "nivel": 1, "vida": 10, "fome": 10, "registrado": 0, "dificuldade": "facil"}

    user_data = inventarios[user_id]
    dificuldade = user_data.get("dificuldade", "normal")

    if quantidade < 0:
        quantidade = int(quantidade * get_difficulty_multiplier(dificuldade, "damage"))

    vida_atual = user_data.get("vida", 10)
    nova_vida = max(0, min(10, vida_atual + quantidade))
    user_data["vida"] = nova_vida
    salvar_inventarios()
    return nova_vida

def alterar_fome(user_id, quantidade):
    """Altera a fome do jogador (positivo para alimentar, negativo para perder fome)."""
    user_id = str(user_id)

    if user_id not in inventarios:
        inventarios[user_id] = {"xp": 0, "nivel": 1, "vida": 10, "fome": 10, "registrado": 0, "dificuldade": "facil"}

    user_data = inventarios[user_id]
    dificuldade = user_data.get("dificuldade", "normal")

    if quantidade < 0:
        quantidade = int(quantidade * get_difficulty_multiplier(dificuldade, "damage"))

    fome_atual = user_data.get("fome", 10)
    nova_fome = max(0, min(10, fome_atual + quantidade))
    user_data["fome"] = nova_fome
    salvar_inventarios()
    return nova_fome

def get_status(user_id):
    """Retorna o status completo do jogador."""
    user_id = str(user_id)

    user_data = inventarios.get(user_id, {"vida": 10, "fome": 10, "xp": 0, "nivel": 1})

    return {
        "vida": user_data.get("vida", 10),
        "fome": user_data.get("fome", 10),
        "xp": user_data.get("xp", 0),
        "nivel": user_data.get("nivel", 1)
    }

XP_VALUES = {
    "galinha": (1, 3),
    "porco": (1, 3),
    "ovelha": (1, 3),
    "vaca": (1, 3),
    "coelho": (1, 2),
    
    "carvao": 2,
    "ferro": 5,
    "ouro": 8,
    "diamante": 15,
    "esmeralda": 20,
    
    "plantio": 1,
    "colheita": 2,
    "pesca": (1, 4),
    "craft": 1
}

def get_precos():
    """Retorna um dicionário com os preços dos itens da loja."""
    return {
        "Bife": 5,
        "Carneiro": 5,
        "Frango": 4,
        "Graveto": 2,
        "Pedregulho": 3,
        "picareta": 10,
        "Tabuacarvalho": 4,
        "Experiencia": 8,
        "Esmeralda": 20
    }

def get_saldo(user_id):
    """Retorna o saldo de esmeraldas do usuário."""
    user_id = str(user_id)
    inventario = inventarios.get(user_id, {})
    return inventario.get("Esmeralda", 0)

def add_esmeraldas(user_id, quantidade):
    """Adiciona ou remove esmeraldas do usuário."""
    user_id = str(user_id)
    if user_id not in inventarios:
        inventarios[user_id] = {}
    inventario = inventarios[user_id]
    nova_qtd = inventario.get("Esmeralda", 0) + quantidade
    if nova_qtd < 0:
        nova_qtd = 0
    inventario["Esmeralda"] = nova_qtd
    salvar_inventarios()

def get_xp_por_atividade(atividade):
    """Retorna a quantidade de XP para uma atividade específica."""
    import random

    xp_data = XP_VALUES.get(atividade.lower(), 0)

    if isinstance(xp_data, tuple):
        min_xp, max_xp = xp_data
        return random.randint(min_xp, max_xp)

    return xp_data

def get_usuarios_com_notificacoes():
    """Retorna lista de user_ids que têm notificações ativadas."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM jogadores WHERE notificacoes = 1')
        return [row[0] for row in c.fetchall()]

def is_registered(user_id):
    """Verifica se o usuário está registrado."""
    user_id = str(user_id)
    user_data = inventarios.get(user_id, {})
    return user_data.get("registrado", 0) == 1

def set_registered(user_id, nome=None):
    """Marca o usuário como registrado."""
    user_id = str(user_id)
    if user_id not in inventarios:
        inventarios[user_id] = {"xp": 0, "nivel": 1, "vida": 10, "fome": 10, "registrado": 0}
    inventarios[user_id]["registrado"] = 1
    if nome:
        inventarios[user_id]["nome"] = nome
    salvar_inventarios()

def set_bioma_atual(user_id, bioma_data):
    """Define o bioma atual do usuário."""
    user_id = str(user_id)
    if user_id not in inventarios:
        inventarios[user_id] = {"xp": 0, "nivel": 1, "vida": 10, "fome": 10, "registrado": 0}
    inventarios[user_id]["bioma_atual"] = bioma_data
    salvar_inventarios()

def get_bioma_atual(user_id):
    """Retorna o bioma atual do usuário."""
    user_id = str(user_id)
    user_data = inventarios.get(user_id, {})
    return user_data.get("bioma_atual")

def set_travel_state(user_id, destination, arrival_time):
    """Define o estado de viagem do usuário."""
    user_id = str(user_id)
    travel_state[user_id] = {
        "destination": destination,
        "arrival_time": arrival_time.isoformat(),
        "traveling": True
    }
    salvar_travel_state()

def get_travel_state(user_id):
    """Retorna o estado de viagem do usuário."""
    user_id = str(user_id)
    return travel_state.get(user_id, {"traveling": False})

def clear_travel_state(user_id):
    """Remove o estado de viagem do usuário."""
    user_id = str(user_id)
    if user_id in travel_state:
        del travel_state[user_id]
        salvar_travel_state()

def is_user_traveling(user_id):
    """Verifica se o usuário está viajando."""
    state = get_travel_state(user_id)
    return state.get("traveling", False)

def get_arrival_time(user_id):
    """Retorna o tempo de chegada do usuário."""
    from datetime import datetime
    state = get_travel_state(user_id)
    if state.get("traveling", False):
        return datetime.fromisoformat(state["arrival_time"])
    return None

def is_command_under_maintenance(command):
    """Verifica se um comando está em manutenção."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('SELECT active FROM maintenance WHERE command = ?', (command,))
        row = c.fetchone()
        return row[0] == 1 if row else False

def set_command_maintenance(command, active):
    """Define se um comando está em manutenção."""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO maintenance (command, active) VALUES (?, ?)', (command, active))
        conn.commit()
