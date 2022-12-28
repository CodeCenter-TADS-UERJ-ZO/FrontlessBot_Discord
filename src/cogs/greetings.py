"""Cog that contains all greetings commands"""

import os
import discord
from dotenv import load_dotenv  # pylint: disable=import-error
from discord.ext import commands
from discord.abc import GuildChannel

# from discord import utils

load_dotenv()
WELCOME_CHANNEL: int = int(os.getenv("DISCORD_WELCOME_CHANNEL"))
discord_bot: discord.Bot = discord.Bot(
    intents=discord.Intents.all()
)  # pylint: disable=no-member


class Greetings(commands.Cog):
    """Cog used to manage all Greeeting interactions"""

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """function that runs when members joins"""
        chan: GuildChannel = self.bot.get_channel(WELCOME_CHANNEL)

        greet_member: str = f"Bem Vindo(a) {member.display_name}"
        embed: discord.Embed = discord.Embed(
            title=greet_member,
            description="Vá ao canal #instruções",
            color=discord.Colour.light_grey(),
        )
        embed.set_author(name=member.display_name, icon_url=member.avatar.url)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"User ID: {member.id}")
        await chan.send(member.mention, embed=embed)


def setup(bot) -> None:
    """Function that sets up the cog for the bot"""
    bot.add_cog(Greetings(bot))
