import discord
from discord import app_commands
from discord.ext import commands
from utils.database import usuarios_coletando, mensagens_coleta

class Parar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="parar", description="Pare de coletar madeira e limpe todas as embeds de coleta")
    async def parar(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        usuarios_coletando.discard(user_id)

        from utils.database import salvar_usuarios_coletando
        salvar_usuarios_coletando()

        mensagens_user = mensagens_coleta.get(user_id, [])
        mensagens_deletadas = 0
        
        for message_data in mensagens_user:
            try:
                channel = self.bot.get_channel(message_data['channel_id'])
                if channel:
                    message = await channel.fetch_message(message_data['message_id'])
                    await message.delete()
                    mensagens_deletadas += 1
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass
        
        if user_id in mensagens_coleta:
            del mensagens_coleta[user_id]
        
        if mensagens_deletadas > 0:
            await interaction.response.send_message(
                f"🚩 Você parou de coletar madeira e {mensagens_deletadas} embed(s) de coleta foram removidas.", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "🚩 Você parou de coletar madeira.", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Parar(bot))
