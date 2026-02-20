import discord
from discord.ext import commands, tasks
from datetime import datetime
from utils.database import inventarios, salvar_inventarios
import asyncio

class Notificacoes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.usuarios_notificados = set()
        self.verificar_plantacoes.start()

    def cog_unload(self):
        self.verificar_plantacoes.cancel()

    @tasks.loop(minutes=5)
    async def verificar_plantacoes(self):
        """Verifica se alguma plantação está pronta e envia notificação por DM"""
        tempo_atual = datetime.now().timestamp()
        
        for user_id, dados in inventarios.items():
            plantacao = dados.get("plantacao_ativa", None)
            
            if plantacao and user_id not in self.usuarios_notificados:
                tempo_colheita = plantacao["tempo_colheita"]
                
                if tempo_atual >= tempo_colheita:
                    try:
                        user = self.bot.get_user(int(user_id))
                        if not user:
                            user = await self.bot.fetch_user(int(user_id))
                        
                        if user:
                            tipo = plantacao["tipo"]
                            emoji = {"trigo": "🌾", "cenoura": "🥕", "batata": "🥔", "beterraba": "🍠"}.get(tipo, "🌱")
                            
                            embed = discord.Embed(
                                title="🌾 Plantação Pronta!",
                                description=f"✅ **{emoji} {tipo.title()} está pronto para colher!**",
                                color=discord.Color.gold()
                            )
                            
                            imagens_maduras = {
                                "trigo": "https://minecraft.wiki/images/2/29/Wheat_Age_7.png",
                                "cenoura": "https://minecraft.wiki/images/8/8b/Carrots_Age_7.png",
                                "batata": "https://minecraft.wiki/images/c/c7/Potatoes_Age_7.png", 
                                "beterraba": "https://minecraft.wiki/images/6/6a/Beetroots_Age_3.png"
                            }
                            embed.set_image(url=imagens_maduras.get(tipo, imagens_maduras["trigo"]))
                            
                            embed.add_field(
                                name="📋 Como colher",
                                value="1️⃣ Use `/perfil`\n2️⃣ Clique em **🌾 Plantar**\n3️⃣ Clique em **🌾 Colher**",
                                inline=False
                            )
                            
                            embed.set_footer(text="MineBlock - Sistema de Plantação")
                            
                            await user.send(embed=embed)
                            
                            self.usuarios_notificados.add(user_id)
                            
                    except discord.Forbidden:
                        pass
                    except Exception as e:
                        print(f"Erro ao enviar notificação para {user_id}: {e}")
            
            elif not plantacao and user_id in self.usuarios_notificados:
                self.usuarios_notificados.discard(user_id)

    @verificar_plantacoes.before_loop
    async def before_verificar_plantacoes(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Notificacoes(bot))
