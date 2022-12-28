"""Frontless Bot

Um bot de gerenciamento para o meu servidor do Discord.

Autores: Mirai
Data de Início: 26/12/2022"""


from pathlib import Path
import os
from dotenv import load_dotenv  # pylint: disable=import-error
import discord


load_dotenv()
TOKEN: str = os.getenv("DISCORD_TOKEN")
bot: discord.Bot = discord.Bot(
    intents=discord.Intents.all()
)  # pylint: disable=no-member


def load_cogs() -> None:
    """Function that Loads all Cogs/Modules of the bot"""
    path: str = f"{Path(__file__).parent}/cogs/"
    dir_list: list[str] = os.listdir(path)
    for i in dir_list:
        if Path(i).suffix == ".py":
            cog: str = i.split(".")[0]
            print(f"Loading {cog = }")
            bot.load_extension(f"cogs.{cog}")


@bot.event
async def on_ready() -> None:
    """function that executes when the bot is ready"""
    print(f"{bot.user} has connected to Discord!")


def main() -> None:
    """Main Function"""
    load_cogs()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
