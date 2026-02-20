import time
from typing import Dict, Any
from utils.database import inventarios, salvar_inventarios

class PlayerData:
    def __init__(self):
        pass

    def get_player(self, user_id: int) -> Dict[str, Any]:
        user_id_str = str(user_id)
        if user_id_str not in inventarios:
            inventarios[user_id_str] = {
                "health": 20,
                "hunger": 20,
                "last_update": int(time.time()),
                "location": None
            }
            salvar_inventarios()
        return inventarios[user_id_str]

    def add_meat(self, user_id: int, amount: int):
        player = self.get_player(user_id)
        player["meat"] += amount

    def add_xp(self, user_id: int, amount: int):
        player = self.get_player(user_id)
        player["xp"] += amount
        pass

player_data = PlayerData()