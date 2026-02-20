import time
import json
import os

TIME_OFFSET_FILE = 'time_offset.json'

def get_time_offset():
    if os.path.exists(TIME_OFFSET_FILE):
        with open(TIME_OFFSET_FILE, 'r') as f:
            data = json.load(f)
            return data.get('offset', 0)
    return 0

def set_time_offset(offset):
    with open(TIME_OFFSET_FILE, 'w') as f:
        json.dump({'offset': offset}, f)

def advance_time(days=1):
    """Advance time by the specified number of days."""
    current_offset = get_time_offset()
    new_offset = current_offset + (days * 2400)
    set_time_offset(new_offset)

def get_minecraft_time():
    """Retorna o tempo atual em Minecraft (MM:SS)."""
    current_time = time.time() + get_time_offset()
    day_length = 2400
    time_in_day = current_time % day_length
    minutes = int(time_in_day // 60)
    seconds = int(time_in_day % 60)

    return f"{minutes:02d}:{seconds:02d}"

def is_night():
    """Verifica se é noite em Minecraft (20:00 - 40:00 no ciclo de 40 min)."""
    current_time = time.time() + get_time_offset()
    day_length = 2400
    time_in_day = current_time % day_length
    minutes = time_in_day / 60
    return minutes >= 20

def get_ticks():
    """Retorna ticks atuais (0-24000)."""
    current_time = time.time() + get_time_offset()
    day_length = 2400
    time_in_day = current_time % day_length
    ticks = (time_in_day / day_length) * 24000
    return int(ticks)