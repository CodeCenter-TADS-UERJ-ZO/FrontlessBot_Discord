"""Frontless Bot

Um bot de gerenciamento para o meu servidor do Discord.

Autores: Mirai
Data de Início: 26/12/2022"""
# pylint: disable=line-too-long

import typing
from pathlib import Path
import os
import asyncio
from dotenv import load_dotenv  # pylint: disable=import-error
import discord
import aiosqlite

#   Essas variaveis são placeholders para quando
#   eu precisar  atualizar os  dados fixos da DB
git_colors: None = None
rules_arr: None = None
db_path: str = f"{Path(__file__).parent.parent}/data/bot_data.db"

load_dotenv()
TOKEN: str | None = os.getenv("DISCORD_TOKEN")
bot_intents: discord.Intents = discord.Intents(
    guilds=True, members=True, bans=True, emojis_and_stickers=True, invites=True
)


bot: discord.Bot = discord.Bot(intents=bot_intents)  # pylint: disable=no-member
bot.db_connected = asyncio.Event()

table_create_commands = [
    "CREATE TABLE IF NOT EXISTS rules(name TEXT, description TEXT, UNIQUE(name, description))",
    "CREATE TABLE IF NOT EXISTS github_colors(name TEXT, color TEXT, UNIQUE(name, color))",
    "CREATE TABLE IF NOT EXISTS active_warns(user_name TEXT, user_discriminator TEXT, user_id INTEGER, reason TEXT, type TEXT, unix_date INTEGER, UNIQUE(user_id))",
    "CREATE TABLE IF NOT EXISTS warns_history(user_name TEXT, user_discriminator TEXT, user_id INTEGER, reason TEXT, type TEXT, unix_date INTEGER)",
    "CREATE TABLE IF NOT EXISTS active_timeouts(user_name TEXT, user_discriminator TEXT, user_id INTEGER, timeout_description TEXT, reason TEXT, level INTEGER, type TEXT, unix_date INTEGER)",
    "CREATE TABLE IF NOT EXISTS timeouts_history(user_name TEXT, user_discriminator TEXT, user_id INTEGER, timeout_description TEXT, reason TEXT, level INTEGER, type TEXT, unix_date INTEGER)",
    "CREATE TABLE IF NOT EXISTS active_bans(user_name TEXT, user_discriminator TEXT, user_id INTEGER, reason TEXT, unix_date INTEGER, UNIQUE(user_id))",
    "CREATE TABLE IF NOT EXISTS ban_history(user_name TEXT, user_discriminator TEXT, user_id INTEGER, reason TEXT, unix_date INTEGER)",
    "CREATE TABLE IF NOT EXISTS programming_languages_roles(role_id INTEGER, role_name TEXT, role_description TEXT, UNIQUE(role_id))",
    "CREATE TABLE IF NOT EXISTS lock_state(role_id INTEGER, channel_id INTEGER, permissions_bin INTEGER, unix_date INTEGER)",
]


def load_cogs() -> None:
    """Function that Loads all Cogs/Modules of the bot"""
    path: str = f"{Path(__file__).parent}/cogs/"
    dir_list: list[str] = os.listdir(path)
    for i in dir_list:
        if Path(i).suffix == ".py":
            cog: str = i.split(".")[0]
            print(f"Loading {cog = }")
            bot.load_extension(f"cogs.{cog}")


async def create_tables(connection) -> None:
    """."""
    if Path(db_path).exists():
        async with connection.cursor() as cursor:
            print("creating tables".upper())
            for i in table_create_commands:
                await cursor.execute(i)
        await connection.commit()


async def add_rules(connection) -> None:
    """."""
    if rules_arr is not None:
        async with connection.cursor() as cursor:
            print("adding rules".upper())
            add_rule_command: str = (
                "INSERT OR IGNORE INTO rules(name, description) VALUES(?,?)"
            )
            for _rule in rules_arr:  # type: ignore pylint: disable=not-an-iterable
                await cursor.execute(add_rule_command, (_rule[0], _rule[1]))
            print("rules added".upper())
        await connection.commit()


async def add_github_colors(connection) -> None:
    """."""
    if git_colors is not None:
        async with connection.cursor() as cursor:
            print("adding github language colors".upper())
            add_rule_command: str = (
                "INSERT OR IGNORE INTO github_colors(name, color) VALUES(?,?)"
            )
            for color_name, _v in git_colors.items():
                color_code: typing.Any = _v["color"]
                if color_code is not None:
                    await cursor.execute(
                        add_rule_command, (color_name.lower(), color_code)
                    )
            print("colors added".upper())
        await connection.commit()


@bot.event
async def on_ready() -> None:
    """function that executes when the bot is ready"""
    bot.db = await aiosqlite.connect(db_path)  # type: ignore
    bot.db_connected.set()
    if Path(db_path).exists():
        await create_tables(bot.db)  # type: ignore
        await add_rules(bot.db)  # type: ignore
        await add_github_colors(bot.db)  # type: ignore
    else:
        print("database does not exists.")
    print(f"{bot.user} has connected to Discord.")


def main() -> None:
    """Main Function"""
    load_cogs()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
