import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f'🔴 Bot conectado como {bot.user}')
    
    print('🧹 Apagando TODOS os comandos globais...')
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
    
    print('🧹 Apagando comandos em servidores...')
    for guild in bot.guilds:
        bot.tree.clear_commands(guild=guild)
        await bot.tree.sync(guild=guild)
    
    print('✅ LIMPEZA COMPLETA!')
    await bot.close()

bot.run(os.getenv("DISCORD_TOKEN"))