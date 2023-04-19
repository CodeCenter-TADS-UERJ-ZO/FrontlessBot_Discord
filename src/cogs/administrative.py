"""Módulo do bot que contém toda a funcionalidade de administração"""
# pylint: disable=all

#   Code should be self descriptive (telling you how)
#   Documentation should tell you how to use and maybe why
#   Comments should tell you why

# ┌─TODOs
# ├┬─[ ] Refactoring
# │└┬──[x] - Error Handling
# │ ├──[ ] - Composition Practices
# │ ├──[x] - Warn User
# │ ├──[x] - Ban User
# │ ├──[x] - Timeout User
# │ ├┬─[x] - Revokes
# │ │├──[x] - Ban (unban)
# │ │├──[x] - Warn
# │ │└──[x] - Timeout
# │ ├──[x] - Rules
# │ ├──[x] - Language Selection Dropdown
# │ ├──[x] - Welcome User
# │ ├┬─[x] - Requests
# │ │├──[x] - Warn
# │ │└──[x] - Timeout
# │ ├┬─[x] - Create Category
# │ │├──[x] - Variables Initializer
# │ │├──[x] - Set Permissions
# │ │├──[x] - Voice Channels
# │ │└──[x] - Text Channels
# │ ├──[x] - Lock Server
# │ ├──[x] - Restore Server
# │ ├──[ ] - DocStrings
# │ ├┬─[ ] - Documentation
# │ │├──[ ] - User
# │ │└──[ ] - Contributor
# │ └┬─[x] - Views/Classes
# │  ├──[x] - TimeOut Dropdown Menu View
# │  ├──[x] - TimeOut Prompt View
# │  ├──[x] - Timeout Accept View
# │  ├──[x] - TimeOut Request View
# │  ├──[x] - Warn Accept View
# │  ├──[x] - Warn Request View
# │  ├──[x] - Role Select
# │  ├──[x] - Persistent View
# │  ├──[x] - Color Selector Modal
# │  ├──[x] - Programming Role Description Modal
# │  ├──[x] - Programming Role Modal
# │  ├──[x] - Ban Confirmation View
# │  └──[x] - User Unban Dropdown
# └┬─[ ] Implement
#  ├──[ ] - Get all-user DataBase data by command (/request_data)
#  ├──[ ] - Request System (Changes, etc...)
#  │   └─>  This will use Forum-Channels and emojis for voting
#  │        The bot will automatically create a "Request" and populate
#  │        with the basic emojis for votinng.
#  ├──[ ] - Guide System (How-To setup something)
#  ├──[ ] - Docs Search (Parse the Docs from a language and search in it.)
#  ├──[ ] - Delete Category (Recursively delete the channels in a category)
#  ├──[ ] - Button selections between University role and Common role.
#  ├──[ ] - Improve Category Creator to create university channels aswell.
#  ├──[ ] - Change welcome screen to reflect changes.
#  ├──[ ] - Checks for auto-modding
#  └──[ ] - (MAYBE) Implement OpenAI ChatGPT3 integration.


# │ ┤ ┐ └ ┴ ┬ ├ ─ ┼ ┘ ┌ •


import typing
from datetime import datetime, timedelta
from time import time
import tomllib
import discord
from discord.ext import commands

from modules.CustomDatabase.CustomDatabase import (  # pylint: disable=import-error
    CustomDatabase,
)
from modules.CustomLogger.CustomLogger import (
    Logger,
)  # pylint: disable=import-error no-name-in-module

# region Variables

BOT_ICON_URL: str = (
    "https://cdn.discordapp.com/app-icons/1056943227183321118/"
    "08902aef3ee87acc3e69081c0a012b71.png?size=2048"
)

MOD_LOGS_CHAN_ID: int = 1092825274439180430
WELCOME_CHAN_ID: int = 1056710866147483760
REQUEST_CHAN_ID: int = 1059280455263850577
RULES_CHAN_ID: int = 1056738639813546034

DEV_ROLE_ID: int = 1058049513111167016
GAME_ROLE_ID: int = 1058052420627857558
EVERYONE_ROLE_ID: int = 1002319287308005396
ADMIN_ROLE_ID: int = 1056755317419028560
UNIVERSITY_ROLE_ID: int = 1090283255699357796

CHANNELS_DELAY: int = 10

ONE_MINUTE = 60
FIVE_MINUTES = 300
TEN_MINUTES = 600
FIFTEEN_MINUTES = 900
THIRTY_MINUTES = 1800
ONE_HOUR = 3600
TWELVE_HOURS = 43200
ONE_DAY = 86400
TWO_DAYS = 172800
ONE_WEEK = 604800

timeout_types: dict[str, list[typing.Union[int, str]]] = {
    "1": [ONE_MINUTE, "1 minuto"],
    "2": [FIVE_MINUTES, "5 minutos"],
    "3": [TEN_MINUTES, "10 minutos"],
    "4": [ONE_HOUR, "1 hora"],
    "5": [ONE_DAY, "1 dia"],
    "6": [ONE_WEEK, "1 semana"],
}

timeout_types_options: list[discord.SelectOption] = [
    discord.SelectOption(
        label=str(_v[1]), value=_k, description=f"O usuário será suspenso por {_v[1]}."
    )
    for _k, _v in timeout_types.items()
]
timeout_types_options.append(
    discord.SelectOption(
        label="Cancelar", value="0", description="Cancela a ação de timeout."
    )
)

timeout_types_options.append(
    discord.SelectOption(
        label="Auto",
        value="-1",
        description="Utiliza o sistema automático de moderação.",
    )
)

# endregion

# region Helper Functions


def hex_to_rgb(hex_code: str) -> tuple[str]:
    """return a tuple with the rgb values of a hex color"""
    _h: str = hex_code.lstrip("#")
    return tuple(int(_h[i : i + 2], 16) for i in (0, 2, 4))


async def user_check(
    user_id: int, context: discord.ApplicationContext, bot: discord.Bot
) -> bool:
    """."""
    return_value: bool = False
    if user_id == context.guild.owner_id:
        await context.respond("Dono do servidor detectado, ação cancelada.")
        return_value = True

    if user_id == bot.user.id:
        await context.respond("FrontlessBot detectado, ação cancelada.")
        return_value = True

    return return_value


async def warn_user_func(
    database: CustomDatabase,
    db_parameters: tuple,
) -> None:  #! To refactor
    """."""
    args: list[str] = [
        "user_name",
        "user_discriminator",
        "user_id",
        "reason",
        "type",
        "unix_date",
    ]

    user_not_warned: bool = True

    tables: list[str] = ["active_warns", "warns_history"]

    user_warn = await database.fetch(
        table=tables[0], search_key="user_id", parameters=db_parameters[2]
    )

    if not user_warn:
        Logger.info("user not found in warn table")
        for table in tables:
            await database.insert(table=table, arguments=args, parameters=db_parameters)
        user_not_warned = True
    else:
        user_not_warned = False

    return user_not_warned


async def timeout_user_func(
    user: discord.User,
    timeout_time: int,
    database: CustomDatabase,
    db_parameters: tuple,
) -> None:
    """."""
    args: list[str] = [
        "user_name",
        "user_discriminator",
        "user_id",
        "timeout_description",
        "reason",
        "level",
        "type",
        "unix_date",
    ]
    tables: list[str] = ["active_timeouts", "timeouts_history"]
    for table in tables:
        await database.insert(table=table, arguments=args, parameters=db_parameters)

    await user.timeout_for(timedelta(seconds=timeout_time))


async def ban_user_func(
    user: discord.User,
    reason: str,
    database: CustomDatabase,
    db_parameters: tuple,
) -> None:
    """."""
    tables: list[str] = ["active_bans", "ban_history"]
    args: list[str] = [
        "user_name",
        "user_discriminator",
        "user_id",
        "reason",
        "unix_date",
    ]
    for table in tables:
        await database.insert(table=table, arguments=args, parameters=db_parameters)

    await user.ban(reason=reason)


# endregion
######################################################
######################################################


async def _create_class_code_voice_channels(
    category: discord.CategoryChannel,
    role: list,
):
    "."


async def _create_code_voice_channels(category: discord.CategoryChannel):
    "..."


class CreateCodeClassView(discord.ui.View):
    def __init__(
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        category: discord.CategoryChannel,
        role: list,
    ):
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.category: discord.CategoryChannel = category
        self.role: list = role

    @discord.ui.button(label="Sim", style=discord.ButtonStyle.success)
    async def yes_button_callback(self, _, interaction: discord.Interaction) -> bool:
        self.stop()
        for i in range(4):
            await self.category.create_voice_channel(name=f"Canal de voz [{i+1:0>2}]")

        for i in range(2):
            st_chan: discord.StageChannel = await self.category.create_stage_channel(
                name=f"Aula Live [{i+1:0>2}]", topic="Aula Live"
            )
            await st_chan.set_permissions(target=self.role[0], overwrite=self.role[1])
            print(f"{st_chan = }")

        await interaction.response.send_message("Canais criados.")

    @discord.ui.button(label="Não", style=discord.ButtonStyle.danger)
    async def no_button_callback(self, _, interaction: discord.Interaction) -> bool:
        self.stop()
        for i in range(4):
            await self.category.create_voice_channel(name=f"Canal de voz [{i+1:0>2}]")

        await interaction.response.send_message("Canais criados.")


class TimeOutDropdownMenuView(discord.ui.View):
    """."""

    def __init__(
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        user: discord.User,
        delete_func: typing.Callable,
        delete_parent_msg_func: typing.Callable,
        reason: str,
        delete_cmd_msg: typing.Callable | None = None,
        database: CustomDatabase,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.user: discord.User = user
        self.delete_func: typing.Callable = delete_func
        self.delete_parent_msg_func: typing.Callable = delete_parent_msg_func
        self.reason: str = reason
        self.delete_cmd_msg: typing.Callable = delete_cmd_msg
        self.database: CustomDatabase = database

    async def _del_msgs(self) -> None:
        if self.delete_func is not None:
            await self.delete_func(delay=1)
        if self.delete_parent_msg_func is not None:
            await self.delete_parent_msg_func(delay=1)
        if self.delete_cmd_msg is not None:
            self.delete_cmd_msg(delete_after=1)

    async def _case_one(
        self,
        selected_value: str,
        interaction: discord.Interaction,
        mod_log_chan: discord.TextChannel,
        timeout_type: str,
    ) -> None:
        self.stop()
        timeout_time: int = int(timeout_types[selected_value][0])
        await self.user.timeout_for(timedelta(seconds=timeout_time))
        timeout_description: str = str(timeout_types[selected_value][1])

        desc_1: str = (
            f"Timeout de {timeout_description} aplicado ao usuário "
            f"{self.user.mention} pelo moderador {interaction.user.mention}."
        )

        timeout_embed: discord.Embed = discord.Embed(
            title="Aviso de timeout",
            description=desc_1,
            colour=discord.Colour.orange(),
            timestamp=datetime.now(),
        )
        timeout_embed.set_thumbnail(url=self.user.avatar.url)

        desc_2: str = (
            f"aplicando timeout de {timeout_description} "
            f"ao usuário {self.user.mention}"
        )
        if mod_log_chan is not None:
            await mod_log_chan.send(embed=timeout_embed)
        else:
            temp_chan = interaction.guild.get_channel(MOD_LOGS_CHAN_ID)
            temp_chan.send(embed=timeout_embed)
        await interaction.response.send_message(
            content=desc_2,
            ephemeral=True,
        )

        await interaction.delete_original_response(delay=2)
        await self._del_msgs()

        parameters = (
            self.user.name,
            self.user.discriminator,
            int(self.user.id),
            timeout_description,
            str(self.reason),
            int(selected_value),
            timeout_type,
            int(time()),
        )

        await timeout_user_func(
            user=self.user,
            database=self.database,
            db_parameters=parameters,
            timeout_time=timeout_time,
        )

    async def _case_two(self, interaction: discord.Interaction) -> None:
        self.stop()
        await interaction.response.send_message(
            "Ignorando violação de diretrizes.", ephemeral=True
        )
        await interaction.delete_original_response(delay=2)
        await self._del_msgs()

    async def _case_three_subcase_one(
        self, interaction: discord.Interaction, max_timeout_types: str | int
    ) -> None:
        timeout_description: str = str(timeout_types[str(max_timeout_types)][1])
        msg: str = (
            f"Usuário já contém um timeout de {timeout_description} "
            "diretrizes implicam que a próxima medida "
            "preventiva seja banimento, deseja aplica-lo?"
        )
        await interaction.response.send_message(
            content=msg,
            view=BanConfirmationView(
                user=self.user,
                delete_func=self.delete_func,
                database=self.database,
                reason=self.reason,
            ),
        )

    async def _case_three_subcase_two(
        self,
        interaction: discord.Interaction,
        mod_log_chan: discord.TextChannel,
        max_user_timeout_type: int,
    ) -> None:
        max_user_timeout_type += 1
        timeout_time: int = int(timeout_types[str(max_user_timeout_type)][0])
        timeout_description: str = str(timeout_types[str(max_user_timeout_type)][1])
        print(f"{timeout_description = }")
        print(f"{timeout_time = }")
        print(f"{max_user_timeout_type = }")

        res: str = (
            f"aplicando timeout de {timeout_description} "
            f"ao usuário {self.user.mention}"
        )
        await interaction.response.send_message(
            content=res,
            ephemeral=True,
        )
        info: str = (
            f"Timeout de {timeout_description} aplicado "
            f"ao usuário {self.user.mention} pelo "
            f"moderador {interaction.user.mention}."
        )
        timeout_embed: discord.Embed = discord.Embed(
            title="Aviso de timeout",
            description=info,
            colour=discord.Colour.orange(),
            timestamp=datetime.now(),
        )
        timeout_embed.set_thumbnail(url=self.user.avatar.url)

        timeout_type = "moderation"

        parameters = (
            self.user.name,
            self.user.discriminator,
            int(self.user.id),
            timeout_description,
            str(self.reason),
            int(max_user_timeout_type),
            timeout_type,
            int(time()),
        )

        await timeout_user_func(
            user=self.user,
            database=self.database,
            db_parameters=parameters,
            timeout_time=timeout_time,
        )

        await mod_log_chan.send(embed=timeout_embed)
        await interaction.delete_original_response(delay=2)
        await self._del_msgs()

    async def _case_three(
        self, interaction: discord.Interaction, mod_log_chan: discord.TextChannel
    ) -> None:
        self.stop()
        user_timeout: list[tuple] = await self.database.fetch(
            table="active_timeouts", search_key="user_id", parameters=self.user.id
        )

        user_timeout_types: list[int] = []
        for i in user_timeout:
            print(i)
            user_timeout_types.append(i[5])

        max_timeout_types: int = max(list(map(int, timeout_types.keys())))
        max_user_timeout_type: int = (
            0 if not user_timeout else int(max(user_timeout_types))
        )
        print(f"{max_user_timeout_type = }")
        if max_user_timeout_type == max_timeout_types:
            await self._case_three_subcase_one(
                interaction=interaction, max_timeout_types=max_timeout_types
            )
        else:
            await self._case_three_subcase_two(
                interaction=interaction,
                mod_log_chan=mod_log_chan,
                max_user_timeout_type=int(max_user_timeout_type),
            )

    @discord.ui.select(
        placeholder="Selecione o Timeout",
        max_values=1,
        min_values=1,
        options=timeout_types_options,
    )
    async def callback_selection(
        self, selection, interaction: discord.Interaction
    ) -> None:
        """."""
        mod_log_chan: discord.TextChannel = interaction.guild.get_channel(
            MOD_LOGS_CHAN_ID
        )
        selected_value: str = str(selection.values[0])
        timeout_type: str = "moderation"

        if selected_value in timeout_types:
            await self._case_one(
                selected_value=selected_value,
                interaction=interaction,
                mod_log_chan=mod_log_chan,
                timeout_type=timeout_type,
            )
        elif selected_value == "0":
            await self._case_two(interaction=interaction)
        else:
            await self._case_three(interaction=interaction, mod_log_chan=mod_log_chan)


class TimeOutPromptView(discord.ui.View):
    """."""

    def __init__(
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        user: discord.User | discord.Member,
        delete_func,
        reason: str,
        database: CustomDatabase,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.user: discord.User = user
        self.delete_func: typing.Any = delete_func
        self.reason: str = reason
        self.database: CustomDatabase = database

    @discord.ui.button(
        label="Sim", style=discord.ButtonStyle.primary, custom_id="yes_timeout"
    )
    async def yes_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        self.stop()
        await interaction.response.send_message(
            content="Selecione o timeout a ser aplicado.",
            view=TimeOutDropdownMenuView(
                delete_func=self.delete_func,
                user=self.user,
                delete_parent_msg_func=interaction.delete_original_response,
                reason=self.reason,
                database=self.database,
            ),
        )

    @discord.ui.button(
        label="Não", style=discord.ButtonStyle.danger, custom_id="no_timeout"
    )
    async def no_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        self.stop()
        await interaction.response.send_message("Ignorando violação de diretrizes.")
        await interaction.delete_original_response(delay=3)
        await self.delete_func(delay=1)


class TimeoutAcceptView(discord.ui.View):
    """."""

    def __init__(
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        reason: str,
        user: discord.User,
        database: CustomDatabase,
        guild: discord.Guild,
        bot: discord.Bot,
        nivel: int,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)

        self.reason: str = reason
        self.user: discord.User = user
        self.database: CustomDatabase = database
        self.guild: discord.Guild = guild
        self.bot: discord.Bot = bot
        self.nivel: int = nivel

    @discord.ui.button(label="Sim", style=discord.ButtonStyle.success)
    async def yes_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        user_id: int = self.user.id
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self, delete_after=60)

        if self.user_check(
            user_id=user_id, context=interaction, guild=self.guild, bot=self.bot
        ):
            return

        await interaction.response.send_message(
            content="Aplicando timeout.", ephemeral=True
        )
        timeout_description: str = timeout_types[str(self.nivel)][1]
        timeout_time: int = timeout_types[str(self.nivel)][0]
        timeout_type: str = "request"

        mod_log_chan: discord.TextChannel = interaction.guild.get_channel(
            MOD_LOGS_CHAN_ID
        )

        parms = (
            self.user.name,
            self.user.discriminator,
            self.user.id,
            timeout_description,
            self.reason,
            self.nivel,
            timeout_type,
            int(time()),
        )

        timeout_user_func(
            user=self.user,
            timeout_time=timeout_time,
            database=self.database,
            db_parameters=parms,
        )

        timeout_embed: discord.Embed = discord.Embed(
            title="Aviso de timeout",
            description=(
                f"Timeout de {timeout_description} aplicado ao ",
                f"usuário {self.user.mention} através de votação da comunidade.",
            ),
            colour=discord.Colour.orange(),
            timestamp=datetime.now(),
        )
        timeout_embed.set_thumbnail(url=self.user.avatar.url)

        await mod_log_chan.send(embed=timeout_embed)

    @discord.ui.button(label="Não", style=discord.ButtonStyle.danger)
    async def no_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        await interaction.response.send_message(
            content="Ignorando request.", ephemeral=True
        )

    async def on_timeout(self) -> None:
        """."""
        for child in self.children:
            child.disabled = True

        await self.message.delete()

    @classmethod
    async def user_check(
        cls,
        user_id: int,
        context: discord.Interaction,
        guild: discord.Guild,
        bot: discord.Bot,
    ) -> bool:
        """."""
        return_value: bool = False
        if user_id == guild.owner_id:
            await context.response.send_message(
                "Dono do servidor detectado, ação cancelada."
            )
            return_value = True

        if user_id == bot.user.id:
            await context.response.send_message(
                "FrontlessBot detectado, ação cancelada."
            )
            return_value = True

        return return_value


class TimoutRequestView(discord.ui.View):
    """."""

    votes: int = 0
    users: list[discord.User] = []

    def __init__(
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        reason: str,
        user: discord.User,
        database: CustomDatabase,
        guild: discord.Guild,
        bot: discord.Bot,
        nivel: int,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.reason: str = reason
        self.user: discord.User = user
        self.database: CustomDatabase = database
        self.guild: discord.Guild = guild
        self.bot: discord.Bot = bot
        self.nivel: int = nivel
        self.interaction_user = None
        self.interaction_channel = None
        self.reseter()

    @discord.ui.button(label="Sim", style=discord.ButtonStyle.success)
    async def yes_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        self.interaction_user: discord.User = interaction.user
        self.interaction_channel: discord.VoiceChannel | discord.StageChannel | discord.TextChannel | discord.ForumChannel | discord.CategoryChannel | discord.Thread | discord.PartialMessageable = (
            interaction.channel
        )
        if interaction.user in self.users:
            await interaction.response.send_message(
                content="Voto já registrado.", ephemeral=True
            )
        else:
            self.incrementer()
            self.appender(interaction.user)
            await interaction.response.send_message(
                content="Voto registrado.",
                ephemeral=True,
            )

    @discord.ui.button(label="Não", style=discord.ButtonStyle.danger)
    async def no_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        self.interaction_user: discord.User = interaction.user
        self.interaction_channel: discord.VoiceChannel | discord.StageChannel | discord.TextChannel | discord.ForumChannel | discord.CategoryChannel | discord.Thread | discord.PartialMessageable = (
            interaction.channel
        )
        if interaction.user in self.users:
            await interaction.response.send_message(
                content="Voto já registrado.", ephemeral=True
            )
        else:
            self.decrementer()
            self.appender(interaction.user)
            await interaction.response.send_message(
                content="Voto registrado.",
                ephemeral=True,
            )

    async def on_timeout(self) -> None:
        """."""
        guild: discord.Guild = self.message.guild
        requests_channel: discord.TextChannel = guild.get_channel(REQUEST_CHAN_ID)
        for child in self.children:
            child.disabled = True

        Logger.info(f"{self.votes = }")
        if self.votes > 0:
            color: discord.Colour = discord.Colour.green()
            desc: str = "Timeout enviado a moderação."
            embed: discord.Embed = discord.Embed(
                title="Resultado", color=color, description=desc
            )
            if self.interaction_user is not None:
                accept_desc: str = (
                    f"Pedido de timeout para o usuário {self.user.mention} requisitado"
                    f"pelo usuário {self.interaction_user.mention}."
                )
            else:
                accept_desc: str = (
                    f"Pedido de timeout para o usuário {self.user.mention} recebido."
                )

            accept_embed: discord.Embed = discord.Embed(
                title="Pedido de timeout.",
                color=discord.Colour.orange(),
                description=accept_desc,
            )

            accept_embed.add_field(name="Razão", value=self.reason)
            accept_embed.add_field(
                name="Tempo", value=timeout_types[str(self.nivel)][1]
            )

            accept_embed.set_author(name="Frontless Programming", icon_url=BOT_ICON_URL)
            accept_embed.set_thumbnail(url=self.user.avatar.url)
            accept_embed.set_footer(
                text=(
                    f"Pedido enviado do canal {self.interaction_channel.name}, na categoria {self.interaction_channel.category.name}"
                ),
                icon_url=BOT_ICON_URL,
            )

            await requests_channel.send(
                embed=accept_embed,
                view=TimeoutAcceptView(
                    reason=self.reason,
                    user=self.user,
                    database=self.database,
                    guild=self.guild,
                    bot=self.bot,
                    timeout=TWO_DAYS,
                    nivel=self.nivel,
                ),
            )
        elif self.votes < 0:
            color: discord.Colour = discord.Colour.red()
            desc: str = "Timeout descartado."

            embed: discord.Embed = discord.Embed(
                title="Resultado", color=color, description=desc
            )
        else:
            color: discord.Colour = discord.Colour.dark_grey()
            desc: str = "votação inconclusiva."
            embed: discord.Embed = discord.Embed(
                title="Resultado", color=color, description=desc
            )

        await self.message.edit(embed=embed, view=self, delete_after=10)

    @classmethod
    def incrementer(cls) -> None:
        """."""
        cls.votes += 1
        Logger.info(f"{cls.votes = }")

    @classmethod
    def decrementer(cls) -> None:
        """."""
        cls.votes -= 1
        Logger.info(f"{cls.votes = }")

    @classmethod
    def appender(cls, user: discord.User) -> None:
        """."""
        cls.users.append(user)

    @classmethod
    def reseter(cls) -> None:
        """."""
        cls.votes = 0
        cls.users.clear()


class RoleSelect(discord.ui.Select):
    """."""

    def __init__(self, options: list[discord.SelectOption], max_val: int) -> None:
        super().__init__(
            placeholder="Selecione suas linguagens",
            max_values=max_val,
            min_values=0,
            options=options,
            custom_id="RoleSelector01",
        )

    def _roles_appender(
        self, values: list[int], user: discord.Member, guild: discord.Guild
    ):
        """."""
        selected_roles: list[discord.Role] = []

        roles_to_add: list[discord.Role] = []
        roles_to_remove: list[discord.Role] = []
        roles_to_add_mentions: list[str] = []
        roles_to_remove_mentions: list[str] = []

        for i in values:
            role: discord.Role = guild.get_role(int(i))
            selected_roles.append(role)

        for _role in selected_roles:
            if _role not in user.roles:
                roles_to_add.append(_role)
                roles_to_add_mentions.append(_role.mention)
            else:
                roles_to_remove.append(_role)
                roles_to_remove_mentions.append(_role.mention)

        roles_add: list[list[discord.Role | str]] = [
            roles_to_add,
            roles_to_add_mentions,
        ]
        roles_remove: list[list[discord.Role | str]] = [
            roles_to_remove,
            roles_to_remove_mentions,
        ]

        return selected_roles, roles_add, roles_remove

    async def callback(self, interaction: discord.Interaction) -> None:
        """."""
        if self.values[0] != "None":
            message: discord.Message = interaction.message
            guild: discord.Guild = interaction.guild
            user: discord.Member = interaction.user
            dev_role: discord.Role = guild.get_role(DEV_ROLE_ID)

            selected_roles, roles_add, roles_remove = self._roles_appender(
                values=self.values, user=user, guild=guild
            )

            if dev_role in user.roles:
                for _role_add in roles_add[0]:
                    await user.add_roles(_role_add)

                for _role_remove in roles_remove[0]:
                    await user.remove_roles(_role_remove)

                adding_str: str = f"adicionando cargos: {', '.join(roles_add[1])}"
                removing_str: str = f"removendo cargos: {', '.join(roles_remove[1])}"
                if len(selected_roles) == 0:
                    message_content: str = "Selecione algum cargo"
                else:
                    if len(roles_remove[1]) == 0:
                        message_content: str = adding_str.capitalize()
                    elif len(roles_add[1]) == 0:
                        message_content: str = removing_str.capitalize()
                    else:
                        message_content: str = (
                            f"{adding_str.capitalize()} e {removing_str.capitalize()}"
                        )
            else:
                message_content = f"Você não tem o cargo {dev_role.mention}"

            if message:
                await interaction.response.send_message(
                    content=message_content,
                    ephemeral=True,
                    delete_after=5,
                )
            else:
                await interaction.edit_original_response(
                    content=message_content,
                    ephemeral=True,
                    delete_after=5,
                )
        else:
            await interaction.response.send_message(
                content="Não há cargos a serem adicionados.",
                ephemeral=True,
                delete_after=5,
            )


class PersistentView(discord.ui.View):  #! To refactor
    """."""

    def __init__(self, options: list[discord.SelectOption], max_val: int) -> None:
        super().__init__(timeout=None)
        self.add_item(RoleSelect(max_val=max_val, options=options))


class ColorSelectorModal(discord.ui.Modal):
    """."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="Insira o código HEX da cor.",
                placeholder="Escreva aqui...",
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Color collected", ephemeral=True)

    async def get_color(self) -> str:
        """."""
        return self.children[0].value


class ProgrammingRoleDescriptionModal(discord.ui.Modal):
    """."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="Insira a descrição do cargo",
                placeholder="Escreva aqui...",
                style=discord.InputTextStyle.long,
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Description collected", ephemeral=True)

    async def get_description(self) -> str:
        """."""
        return self.children[0].value


class ProgrammingRoleModal(discord.ui.Modal):
    """."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args,
            **kwargs,
        )
        self.add_item(
            discord.ui.InputText(
                label="Insira o código HEX da cor.",
                placeholder="Escreva aqui...",
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Insira a descrição do cargo",
                placeholder="Escreva aqui...",
                style=discord.InputTextStyle.long,
            )
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            "Role Attributes Collected", ephemeral=True
        )

    async def get_color(self) -> str:
        """."""
        return self.children[0].value

    async def get_description(self) -> str:
        """."""
        return self.children[1].value


class BanConfirmationView(discord.ui.View):
    """."""

    def __init__(
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        user: discord.User,
        delete_func,
        reason: str,
        database: CustomDatabase,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.user: discord.User = user
        self.delete_func: typing.Any = delete_func
        self.reason: str = reason
        self.database: CustomDatabase = database

    @discord.ui.button(
        label="Sim", style=discord.ButtonStyle.primary, custom_id="yes_ban_button"
    )
    async def yes_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        self.stop()
        guild: discord.Guild = interaction.guild
        mod_usr: discord.User = interaction.user
        target_usr: discord.User = self.user
        mod_log_chan: discord.TextChannel = guild.get_channel(MOD_LOGS_CHAN_ID)
        epoch_date: int = int(time())
        params: tuple = (
            str(target_usr.name),
            str(target_usr.discriminator),
            int(target_usr.id),
            self.reason,
            epoch_date,
        )

        desc: str = (
            "Banimento aplicado ao usuário "
            f"{target_usr.mention} "
            f"pelo moderador {mod_usr.mention}."
        )
        timeout_embed: discord.Embed = discord.Embed(
            title="Aviso de banimento",
            description=desc,
            colour=discord.Colour.red(),
            timestamp=datetime.now(),
        )
        timeout_embed.set_thumbnail(url=target_usr.avatar.url)
        await mod_log_chan.send(embed=timeout_embed)
        await interaction.response.send_message(
            content=f"Banindo {target_usr.mention}.", ephemeral=True
        )
        await ban_user_func(
            user=target_usr,
            reason=self.reason,
            database=self.database,
            db_parameters=params,
        )

        await interaction.delete_original_response(delay=3)
        await self.delete_func(delay=1)

    @discord.ui.button(
        label="Não", style=discord.ButtonStyle.danger, custom_id="no_ban_button"
    )
    async def no_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        self.stop()
        await interaction.response.send_message("Ignorando violação de diretrizes.")
        await interaction.delete_original_response(delay=3)
        await self.delete_func(delay=1)


class UserUnbanDropdown(discord.ui.Select):  #! To refactor
    """."""

    def __init__(
        self,
        options: list[discord.SelectOption],
        max_val: int,
        delete_func: typing.Callable,
        reason: str,
        bans: list[discord.User],
        database: CustomDatabase,
    ) -> None:
        super().__init__(
            placeholder="Selecione o usuário.",
            max_values=max_val,
            min_values=0,
            options=options,
        )
        self.delete_func: typing.Callable = delete_func
        self.reason: str = reason
        self.bans: list[discord.User] = bans
        self.database: CustomDatabase = database

    async def callback(self, interaction: discord.Interaction) -> None:
        """."""
        welcome_channel: discord.TextChannel = interaction.guild.get_channel(
            WELCOME_CHAN_ID
        )
        invite: discord.Invite = await welcome_channel.create_invite(
            max_uses=1, max_age=TWO_DAYS
        )
        for i in self.bans:
            if int(self.values[0]) == i.id:
                unban_user: discord.User = i

        mod_log_chan: discord.TextChannel = interaction.guild.get_channel(
            MOD_LOGS_CHAN_ID
        )
        revoke_embed: discord.Embed = discord.Embed(
            title="Aviso da moderação",
            description=f"Banimento do usuário {unban_user.mention} revogado pelo moderador {interaction.user.mention}.",
            colour=discord.Colour.dark_grey(),
            timestamp=datetime.now(),
        )
        revoke_embed.set_thumbnail(url=unban_user.avatar.url)

        await mod_log_chan.send(embed=revoke_embed)
        await interaction.guild.unban(user=unban_user)
        await interaction.response.send_message(
            f"Ban do usuário {unban_user.mention} revogado."
        )
        await unban_user.send(
            f"Seu ban na {interaction.guild.name} foi revogado, para voltar ao servidor acesse este link: {invite.url}, ele ficará disponível por 48 horas."
        )

        await self.database.delete_where(
            table="active_bans", search_key="user_id", parameters=unban_user.id
        )


class WarnAcceptView(discord.ui.View):
    """."""

    def __init__(
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        reason: str,
        user: discord.User,
        database: CustomDatabase,
        guild: discord.Guild,
        bot: discord.Bot,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.reason: str = reason
        self.user: discord.User = user
        self.database: CustomDatabase = database
        self.guild: discord.Guild = guild
        self.bot: discord.Bot = bot

    @discord.ui.button(label="Sim", style=discord.ButtonStyle.success)
    async def yes_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        user_id: int = self.user.id
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self, delete_after=60)
        if await self.user_check(
            user_id=int(user_id), context=interaction.response, bot=self.bot
        ):
            return

        await interaction.response.send_message(
            content="Aplicando aviso.", ephemeral=True
        )
        parms: tuple = (
            self.user.name,
            self.user.discriminator,
            int(self.user.id),
            self.reason,
            "request",
            int(time()),
        )

        if await warn_user_func(database=self.database, db_parameters=parms):
            mod_log_chan: discord.TextChannel = interaction.guild.get_channel(
                MOD_LOGS_CHAN_ID
            )
            timeout_embed: discord.Embed = discord.Embed(
                title="Aviso da moderação",
                description=(
                    f"{self.user.mention}, este é um aviso da moderação, "
                    "a proxima sinalização será provida de um timeout."
                ),
                colour=discord.Colour.yellow(),
                timestamp=datetime.now(),
            )
            timeout_embed.set_thumbnail(url=self.user.avatar.url)
            await mod_log_chan.send(embed=timeout_embed)
            await interaction.response.send_message(
                content="Aplicando aviso ao usuário", ephemeral=True
            )
        else:
            await interaction.followup.send(
                content=f"usuário {self.user.mention} já previamente avisado.",
                ephemeral=True,
            )

    @discord.ui.button(label="Não", style=discord.ButtonStyle.danger)
    async def no_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        await interaction.response.send_message(
            content="Ignorando request.", ephemeral=True
        )

    async def on_timeout(self) -> None:
        """."""
        for child in self.children:
            child.disabled = True

        await self.message.delete()

    @classmethod
    async def user_check(
        cls, user_id: int, context: discord.ApplicationContext, bot: discord.Bot
    ) -> bool:
        """."""
        return_value: bool = False
        if user_id == context.guild.owner_id:
            await context.send_message("Dono do servidor detectado, ação cancelada.")
            return_value = True

        if user_id == bot.user.id:
            await context.send_message("FrontlessBot detectado, ação cancelada.")
            return_value = True

        return return_value


class WarnRequestView(discord.ui.View):
    """."""

    votes: int = 0
    users: list[discord.User] = []

    def __init__(
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        reason: str,
        user: discord.User,
        database: CustomDatabase,
        bot: discord.Bot,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.reason: str = reason
        self.user: discord.User = user
        self.database: CustomDatabase = database
        self.bot: discord.Bot = bot
        self.reseter()

    @discord.ui.button(label="Sim", style=discord.ButtonStyle.success)
    async def yes_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        self.interaction_user: discord.User = (  # pylint: disable=attribute-defined-outside-init
            interaction.user
        )
        self.interaction_channel: typing.Union[  # pylint: disable=attribute-defined-outside-init
            discord.VoiceChannel,
            discord.StageChannel,
            discord.TextChannel,
            discord.ForumChannel,
            discord.CategoryChannel,
            discord.Thread,
            discord.PartialMessageable,
        ] = interaction.channel
        if interaction.user in self.users:
            await interaction.response.send_message(
                content="Voto já registrado.", ephemeral=True
            )
        else:
            self.incrementer()
            self.appender(interaction.user)
            await interaction.response.send_message(
                content="Voto registrado.",
                ephemeral=True,
            )

    @discord.ui.button(label="Não", style=discord.ButtonStyle.danger)
    async def no_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        self.interaction_user: discord.User = (  # pylint: disable=attribute-defined-outside-init
            interaction.user
        )
        self.interaction_channel: typing.Union[  # pylint: disable=attribute-defined-outside-init
            discord.VoiceChannel,
            discord.StageChannel,
            discord.TextChannel,
            discord.ForumChannel,
            discord.CategoryChannel,
            discord.Thread,
            discord.PartialMessageable,
        ] = interaction.channel
        if interaction.user in self.users:
            await interaction.response.send_message(
                content="Voto já registrado.", ephemeral=True
            )
        else:
            self.decrementer()
            self.appender(interaction.user)
            await interaction.response.send_message(
                content="Voto registrado.",
                ephemeral=True,
            )

    async def on_timeout(self) -> None:
        """."""
        guild: discord.Guild = self.message.guild
        requests_channel: discord.TextChannel = guild.get_channel(REQUEST_CHAN_ID)
        for child in self.children:
            child.disabled = True

        Logger.info(f"{self.votes = }")
        if self.votes > 0:
            color: discord.Colour = discord.Colour.green()
            desc: str = "Aviso enviado a moderação."
            embed: discord.Embed = discord.Embed(
                title="Resultado", color=color, description=desc
            )
            if self.interaction_user is not None:
                accept_desc: str = (
                    f"Pedido de aviso para o usuário {self.user.mention}"
                    f" requisitado pelo usuário {self.interaction_user.mention}."
                )
            else:
                accept_desc: str = (
                    f"Pedido de aviso para o usuário {self.user.mention} recebido."
                )

            accept_embed: discord.Embed = discord.Embed(
                title="Pedido de aviso.",
                color=discord.Colour.yellow(),
                description=accept_desc,
            )

            accept_embed.add_field(name="Razão", value=self.reason)

            accept_embed.set_author(name="Frontless Programming", icon_url=BOT_ICON_URL)
            accept_embed.set_thumbnail(url=self.user.avatar.url)
            accept_embed.set_footer(
                text=(
                    f"Pedido enviado do canal {self.interaction_channel.name}, "
                    f"na categoria {self.interaction_channel.category.name}"
                ),
                icon_url=BOT_ICON_URL,
            )

            await requests_channel.send(
                embed=accept_embed,
                view=WarnAcceptView(
                    timeout=TWO_DAYS,
                    database=self.database,
                    reason=self.reason,
                    guild=guild,
                    user=self.user,
                    bot=self.bot,
                ),
            )
        elif self.votes < 0:
            color: discord.Colour = discord.Colour.red()
            desc: str = "Aviso descartado."

            embed: discord.Embed = discord.Embed(
                title="Resultado", color=color, description=desc
            )
        else:
            color: discord.Colour = discord.Colour.dark_grey()
            desc: str = "votação inconclusiva."
            embed: discord.Embed = discord.Embed(
                title="Resultado", color=color, description=desc
            )

        await self.message.edit(embed=embed, view=self, delete_after=10)

    @classmethod
    def incrementer(cls) -> None:
        """."""
        cls.votes += 1
        Logger.info(f"{cls.votes = }")

    @classmethod
    def decrementer(cls) -> None:
        """."""
        cls.votes -= 1
        Logger.info(f"{cls.votes = }")

    @classmethod
    def appender(cls, user: discord.User) -> None:
        """."""
        cls.users.append(user)

    @classmethod
    def reseter(cls) -> None:
        """."""
        cls.votes = 0
        cls.users.clear()


class UserUnbanView(discord.ui.View):
    """."""

    def __init__(
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        delete_func,
        reason: str,
        database: CustomDatabase,
        options: list,
        max_val: int,
        bans: list[discord.User],
    ) -> None:
        super().__init__(timeout=None)

        self.add_item(
            UserUnbanDropdown(
                max_val=max_val,
                options=options,
                database=database,
                delete_func=delete_func,
                reason=reason,
                bans=bans,
            )
        )


######################################################
######################################################


class Adminstrative(commands.Cog):
    """Cog used to manage all Administrative commands"""

    def __init__(self, bot) -> None:
        self.bot = bot
        self.bot.persistent_views_added = False

    @commands.slash_command(name="regras", description="Exibe as regras")
    @commands.has_role(ADMIN_ROLE_ID)
    async def regras(self, ctx: discord.ApplicationContext) -> None:  #! To refactor
        """Função que exibe as regras do servidor"""
        rules: list[tuple[str, str]] = await self.bot.db.fetch(table="rules")
        embed: discord.Embed = discord.Embed(
            title="Regras",
            description="Estas são as regras do servidor.",
            color=discord.Colour.light_grey(),
            timestamp=datetime.now(),
        )
        for _rule in rules:
            embed.add_field(name=_rule[0], value=_rule[1], inline=False)
        embed.set_author(name="Frontless Programming", icon_url=BOT_ICON_URL)
        embed.set_thumbnail(url=BOT_ICON_URL)
        embed.set_footer(text="Feito pela comunidade com ❤️.", icon_url=BOT_ICON_URL)

        await ctx.respond(embed=embed)

    @commands.slash_command(
        name="language_selection",
        description="Displays the dropdown for the language selection",
    )
    @commands.has_role(ADMIN_ROLE_ID)
    async def language_selection(
        self, ctx: discord.ApplicationContext
    ) -> None:  #! To Refactor
        """Displays the dropdown for the language selection"""

        options: list[discord.SelectOption] = []
        roles: list[tuple[str, str, str]] = await self.bot.db.fetch(
            table="programming_languages_roles",
        )

        if roles == []:
            opt: discord.SelectOption = discord.SelectOption(
                value="None", label="Empty", description="Empty"
            )
            mx_len: int = 1
            options.append(opt)
        else:
            for i in roles:
                opt: discord.SelectOption = discord.SelectOption(
                    value=str(i[0]), label=str(i[1]), description=str(i[2])
                )
                options.append(opt)
                mx_len: int = len(options)

        if ctx.message:
            await ctx.edit(
                view=PersistentView(max_val=mx_len, options=options),
            )
        else:
            await ctx.respond(
                view=PersistentView(max_val=mx_len, options=options),
            )

    # region Create Category
    async def _create_category_create_variables_initializer(
        self,
        ctx: discord.ApplicationContext,
        category_name: str,
        category_type: str,
    ) -> None:
        """."""
        Logger().info("initializing variables")
        guild: discord.Guild = ctx.guild
        database: CustomDatabase = self.bot.db
        Logger().info(f"{guild = }")

        category: discord.CategoryChannel = await guild.create_category(
            name=category_name
        )
        Logger().info(f"{category = }")
        Logger().info("creating roles")

        everyone_role: discord.Role = guild.get_role(EVERYONE_ROLE_ID)

        if category_type.lower() == "code":
            role_tuple: list[tuple[str, str]] = await database.fetch(
                table="github_colors",
                search_key="name",
                parameters=category_name.lower(),
            )
            print(role_tuple[0])

            if role_tuple:
                role: str = role_tuple[0]
                role_color_tuple: tuple[str] = hex_to_rgb(role[1])
                role_base: discord.Role = await guild.create_role(
                    name=role[0].capitalize(),
                    color=discord.Colour.from_rgb(
                        role_color_tuple[0], role_color_tuple[1], role_color_tuple[2]
                    ),
                )
            else:
                modal: ProgrammingRoleModal = ProgrammingRoleModal(
                    title="Programming Category"
                )
                await ctx.send_modal(modal)
                if await modal.wait():
                    hex_color: str = await modal.get_color()
                    role_color_tuple: tuple[str] = hex_to_rgb(hex_color)
                    role_base: discord.Role = await guild.create_role(
                        name=category_name.capitalize(),
                        color=discord.Colour.from_rgb(
                            role_color_tuple[0],
                            role_color_tuple[1],
                            role_color_tuple[2],
                        ),
                    )
                    role_description: str = await modal.get_description()
                    _args: list[str] = [
                        "role_id",
                        "role_name",
                        "role_description",
                    ]
                    _parms = (int(role_base.id), role_base.name, role_description)

                    await self.bot.db.insert(
                        table="programming_languages_roles",
                        arguments=_args,
                        parameters=_parms,
                    )

                    Logger().info(f"{role_base = }")
                    stage_adm_role: discord.Role | None = await guild.create_role(
                        name=f"Administrador de Palcos [{role_base.name}]",
                        color=discord.Colour.darker_grey(),
                    )
                    Logger().info(f"{stage_adm_role = }")
        else:
            modal: ColorSelectorModal = ColorSelectorModal(title="ColorPicker")
            await ctx.send_modal(modal)
            if await modal.wait():
                hex_color: str = await modal.get_color()
                role_color_tuple: tuple[str] = hex_to_rgb(hex_color)
                role_base: discord.Role = await guild.create_role(
                    name=category_name.capitalize(),
                    color=discord.Colour.from_rgb(
                        role_color_tuple[0],
                        role_color_tuple[1],
                        role_color_tuple[2],
                    ),
                )
                role_base: discord.Role = await guild.create_role(name=category_name)
                Logger().info(f"{role_base = }")
                stage_adm_role = None
                Logger().info(f"{stage_adm_role = }")

        Logger().info("setting roles permissions")

        everyone_permissions: discord.PermissionOverwrite = discord.PermissionOverwrite(
            view_channel=False,
            connect=False,
        )
        Logger().info(f"{everyone_permissions = }")

        role_permissions: discord.PermissionOverwrite = discord.PermissionOverwrite(
            view_channel=True,
            connect=True,
        )
        Logger().info(f"{role_permissions = }")

        roles: list = [everyone_role, role_base]

        permissions: list = [
            everyone_permissions,
            role_permissions,
        ]

        if category_type.lower() == "code":
            stage_adm_role_permissions: discord.PermissionOverwrite | None = (
                discord.PermissionOverwrite(
                    connect=True,
                    view_channel=True,
                    manage_channels=True,
                    move_members=True,
                    mute_members=True,
                )
            )
            Logger().info(f"{stage_adm_role_permissions = }")
            permissions.append(stage_adm_role_permissions)
        else:
            permissions.append(None)

        if category_type.lower() == "facul":
            university_role: discord.Role = await guild.get_role(UNIVERSITY_ROLE_ID)
            university_permissions: discord.PermissionOverwrite = (
                discord.PermissionOverwrite(
                    view_channel=True,
                    connect=True,
                )
            )
            roles.append(university_role)
            permissions.append(university_permissions)
        else:
            permissions.append(None)
            roles.append(None)

        return [
            category,
            roles,
            permissions,
        ]

    async def _create_category_set_permissions(
        self,
        category: discord.CategoryChannel,
        roles: list,
        permissions: list,
        category_type: str,
    ) -> None:
        """."""

        Logger().info("setting permissions in category")
        print(roles)
        print(permissions)

        await category.set_permissions(target=roles[0], overwrite=permissions[0])
        await category.set_permissions(target=roles[1], overwrite=permissions[1])
        if category_type.lower() == "code":
            if roles[2] is not None:
                await category.set_permissions(
                    target=roles[2], overwrite=permissions[2]
                )

        if category_type.lower() == "facul":
            await category.set_permissions(target=roles[3], overwrite=permissions[3])

    async def _create_category_create_voice_channels(
        self,
        ctx: discord.ApplicationContext,
        category: discord.CategoryChannel,
        role: list,
        category_type: str,
    ) -> None:
        """Helper function that creates the voice channels in the category_creator command."""

        Logger().info("creating voice channels")
        await ctx.respond("Criando canais de voz")
        if category_type.lower() == "code":
            await ctx.respond(
                "Esta categoria será usada para as aulas?",
                view=CreateCodeClassView(category=category, role=role),
            )

        elif category_type.lower() == "game":
            for i in range(4):
                duo_vc: discord.VoiceChannel = await category.create_voice_channel(
                    name=f"Duo {i+1:0>2}"
                )
                await duo_vc.edit(user_limit=2)

            for i in range(2):
                squad_vc: discord.VoiceChannel = await category.create_voice_channel(
                    name=f"Squad {i+1:0>2}"
                )
                await squad_vc.edit(user_limit=4)

            for i in range(4):
                await category.create_voice_channel(name=f"Livre {i+1:0>2}")
        else:
            for i in range(4):
                await category.create_voice_channel(name=f"Canal de voz {i+1:0>2}")

    async def _create_category_create_text_channels(
        self,
        ctx: discord.ApplicationContext,
        category: discord.CategoryChannel,
        category_type: str,
    ) -> None:
        """Helper function that creates the voice channels in the category_creator command."""

        Logger().info("creating text channels")
        await ctx.respond("Criando canais de texto")

        w_chan: discord.TextChannel = await category.create_text_channel(
            name="boas-vindas"
        )
        Logger().info(f"{w_chan = }")

        r_chan: discord.TextChannel = await category.create_text_channel(name="regras")
        Logger().info(f"{r_chan = }")

        g_chan: discord.TextChannel = await category.create_text_channel(name="geral")
        Logger().info(f"{g_chan = }")

        await w_chan.move(beginning=True)
        await r_chan.move(after=w_chan)
        await g_chan.move(after=r_chan)

        await w_chan.edit(slowmode_delay=CHANNELS_DELAY)
        await r_chan.edit(slowmode_delay=CHANNELS_DELAY)
        await g_chan.edit(slowmode_delay=CHANNELS_DELAY)

        if category_type.lower() in ("code", "facul"):
            s_chan: discord.ForumChannel = await category.create_forum_channel(
                name="suporte"
            )
            Logger().info(f"{s_chan = }")
            await s_chan.move(after=g_chan)
            await s_chan.edit(slowmode_delay=CHANNELS_DELAY)

    @commands.slash_command(
        name="create_category",
        description="Cria uma categoria, os cargos e configura todos os canais",
    )
    @commands.has_role(ADMIN_ROLE_ID)
    async def create_category(
        self, ctx: discord.ApplicationContext, name: str, category_type: str
    ) -> None:
        """Comando de gerenciamento de categorias, especifico para as categorias de linguagem
        tem como argumento o nome da linguagem em questão e cria todos os canais base da categoria
        além de criar o cargo e configurar as permissões."""

        if category_type not in ("code", "game", "facul"):
            await ctx.response.send_message("Tipo da categoria não reconhecido.")
            return

        [
            category,
            roles,
            permissions,
        ] = await self._create_category_create_variables_initializer(
            ctx=ctx,
            category_name=name,
            category_type=category_type,
        )

        await self._create_category_set_permissions(
            category=category,
            category_type=category_type,
            roles=roles,
            permissions=permissions,
        )

        await self._create_category_create_text_channels(
            ctx=ctx, category=category, category_type=category_type
        )

        stage_admin_role_tuple: tuple = (roles[2], permissions[2])
        await self._create_category_create_voice_channels(
            ctx=ctx,
            category=category,
            role=stage_admin_role_tuple,
            category_type=category_type,
        )

        for chan in category.channels:
            if not chan.permissions_synced:
                await chan.edit(sync_permissions=True)

        Logger().info("done")
        if roles[2] is not None:
            await ctx.respond(
                (
                    f"Categoria {category.name}, e os cargos {roles[1].mention}"
                    f" e {roles[2].mention} foram criados."
                ),
            )
        else:
            await ctx.respond(
                (
                    f"Categoria {category.name}, e o cargo {roles[1].mention} foi criado."
                ),
            )

    # endregion

    @commands.slash_command(name="welcome", description="Exibe a tela de boas-vindas")
    @commands.has_role(ADMIN_ROLE_ID)
    async def welcome(self, ctx: discord.ApplicationContext) -> None:  #! To refactor
        """."""
        guild: discord.Guild = ctx.guild
        rule_channel: discord.TextChannel = guild.get_channel(RULES_CHAN_ID)
        dev_role: discord.Role = guild.get_role(DEV_ROLE_ID)
        game_role: discord.Role = guild.get_role(GAME_ROLE_ID)
        embed_intro: discord.Embed = discord.Embed(
            type="article",
            timestamp=datetime.now(),
            title="Bem-vindo(a)",
            color=discord.Colour.light_grey(),
        )
        embed_intro.add_field(
            name="Leia-me",
            value=f"""Nessa comunidade programadores se reunem para conversar, estudar e interagir entre si. Recomendo dar uma lida nas {rule_channel.mention} para ter certeza de que você não vai levar um timeout por engano.

            **Siga as instruções abaixo para ter acesso ao servidor**
            """,
            inline=False,
        )
        embed_intro.add_field(
            name="Cargos de desenvolvedor.",
            value=f"""
            Para poder selecionar um cargo de desenvoledor você deverá primeiro obter o cargo base {dev_role.mention} e ele só será obtido pelo usuários que sincronizarem a conta do GitHub com o Discord.

            Se você já possui a conta sincronizada, então vá para o menu do servidor e acesse *"Cargos vinculados..."*.
            """,
            inline=False,
        )
        embed_intro.add_field(
            name="Cargo de jogos.",
            value=f"""Para o cargo de {game_role.mention}, você deve ter vinculado alguma das seguintes contas:
            • PlayStation Network
            • Twitch
            • Riot Games
            • Xbox
            • Epic Games
            • Steam
            • League of Legends
            • Battle.net

        É claro que você pode ter ambos os cargos, basta preencher os requisitos.
        """,
            inline=False,
        )
        embed_intro.set_author(name="Frontless Programming")
        embed_intro.set_thumbnail(url=BOT_ICON_URL)
        embed_intro.set_footer(
            text="Um abraço da FrontlessTeam. ❤️.", icon_url=BOT_ICON_URL
        )

        if ctx.message:
            await ctx.edit(
                embed=embed_intro,
            )
        else:
            await ctx.respond(
                embed=embed_intro,
            )

    @commands.slash_command(
        name="warn_user", description="Warns the user [just one time]"
    )
    @commands.has_role(ADMIN_ROLE_ID)
    async def warn_user(
        self,
        ctx: discord.ApplicationContext,
        user: discord.User,
        reason: str,
    ) -> None:
        """."""
        if await user_check(user_id=int(user.id), context=ctx, bot=self.bot):
            return

        database: CustomDatabase = self.bot.db
        parms = (
            user.name,
            user.discriminator,
            int(user.id),
            reason,
            "moderation",
            int(time()),
        )

        if await warn_user_func(database=database, db_parameters=parms):
            mod_log_chan: discord.TextChannel = ctx.guild.get_channel(MOD_LOGS_CHAN_ID)
            timeout_embed: discord.Embed = discord.Embed(
                title="Aviso da moderação",
                description=(
                    f"{user.mention}, este é um aviso da moderação, "
                    "a proxima sinalização será provida de um timeout."
                ),
                colour=discord.Colour.yellow(),
                timestamp=datetime.now(),
            )
            timeout_embed.set_thumbnail(url=user.avatar.url)

            await mod_log_chan.send(embed=timeout_embed)
            await ctx.respond(f"Aviso aplicado ao usuário {user.mention}.")
        else:
            await ctx.respond(
                f"usuário {user.mention} já previamente avisado, aplicar timeout?",
                view=TimeOutPromptView(
                    database=database, reason=reason, user=user, delete_func=ctx.delete
                ),
            )

    @commands.slash_command(name="remove_warn", description="Revokes the warning")
    @commands.has_role(ADMIN_ROLE_ID)
    async def remove_warn(  #! To refactor
        self, ctx: discord.ApplicationContext, user: discord.User
    ) -> None:
        """."""
        if await user_check(user_id=int(user.id), context=ctx, bot=self.bot):
            return

        user_id: int = user.id
        database: CustomDatabase = self.bot.db
        user_warned = await database.fetch(
            table="active_warns", search_key="user_id", parameters=user_id
        )

        if not user_warned:
            print("user not found in warn table")
            await ctx.respond(
                f"O usuário {user.mention} não tem nenhum aviso no banco de dados."
            )
        else:
            await database.delete_where(
                table="active_warns", search_key="user_id", parameters=user_id
            )
            mod_log_chan: discord.TextChannel = ctx.guild.get_channel(MOD_LOGS_CHAN_ID)
            revoke_warn_embed: discord.Embed = discord.Embed(
                title="Aviso da moderação",
                description=f"aviso do {user.mention} revogado pelo moderador {ctx.user.mention}.",
                colour=discord.Colour.darker_grey(),
                timestamp=datetime.now(),
            )
            revoke_warn_embed.set_thumbnail(url=user.avatar.url)

            await mod_log_chan.send(embed=revoke_warn_embed)
            await ctx.respond(f"Removendo aviso do usuário {user.mention}.")

    @commands.slash_command(name="warn_request", description="Requests a user warning")
    async def warn_request(  #! To refactor
        self, ctx: discord.ApplicationContext, user: discord.User, reason: str
    ) -> None:
        """."""
        if await user_check(user_id=int(user.id), context=ctx, bot=self.bot):
            return

        embed: discord.Embed = discord.Embed(
            color=discord.Colour.yellow(),
            timestamp=datetime.now(),
            title="Votação de aviso.",
            description=f"Usuário: {user.mention}",
        )

        embed.add_field(name="Motivo", value=reason)

        await ctx.respond(
            embed=embed,
            view=WarnRequestView(
                user=user,
                reason=reason,
                database=self.bot.db,
                timeout=THIRTY_MINUTES,
                bot=self.bot,
            ),
        )

    @commands.slash_command(name="timeout_user", description="Timeouts the user")
    @commands.has_role(ADMIN_ROLE_ID)
    async def timeout_user(
        self,
        ctx: discord.ApplicationContext,
        user: discord.User,
        reason: str,
    ) -> None:
        """."""
        if await user_check(user_id=int(user.id), context=ctx, bot=self.bot):
            return

        await ctx.response.send_message(
            content="Selecione o timeout a ser aplicado.",
            view=TimeOutDropdownMenuView(
                delete_func=ctx.delete,
                user=user,
                delete_parent_msg_func=None,
                reason=reason,
                database=self.bot.db,
            ),
        )

    @commands.slash_command(name="revoke_timeout", description="Timeouts the user")
    @commands.has_role(ADMIN_ROLE_ID)
    async def revoke_timeout(  #! To refactor
        self,
        ctx: discord.ApplicationContext,
        user: discord.User,
    ) -> None:
        """."""
        if await user_check(user_id=int(user.id), context=ctx, bot=self.bot):
            return

        database: CustomDatabase = self.bot.db
        await database.delete_where(
            table="active_timeouts", search_key="user_id", parameters=int(user.id)
        )
        mod_log_chan: discord.TextChannel = ctx.guild.get_channel(MOD_LOGS_CHAN_ID)

        revoke_timeout_embed: discord.Embed = discord.Embed(
            title="Aviso da moderação",
            description=f"Timeout do {user.mention} revogado pelo moderador {ctx.user.mention}.",
            colour=discord.Colour.darker_grey(),
            timestamp=datetime.now(),
        )
        revoke_timeout_embed.set_thumbnail(url=user.avatar.url)

        await mod_log_chan.send(embed=revoke_timeout_embed)
        await ctx.respond(f"Removido timeout do {user.mention}")

    @commands.slash_command(name="timeout_request", description="Timeouts the user")
    async def timeout_request(  #! To refactor
        self,
        ctx: discord.ApplicationContext,
        user: discord.User,
        reason: str,
        nivel: int,
    ) -> None:
        """."""
        if await user_check(user_id=int(user.id), context=ctx, bot=self.bot):
            return

        embed: discord.Embed = discord.Embed(
            color=discord.Colour.orange(),
            timestamp=datetime.now(),
            title="Votação de Timeout.",
            description=f"Usuário: {user.mention}",
        )

        if int(nivel) < 4:
            timeout_time: str = timeout_types[str(nivel)][1]
            embed.add_field(name="Motivo", value=reason, inline=False)
            embed.add_field(name="Tempo", value=timeout_time, inline=False)

            await ctx.respond(
                embed=embed,
                view=TimoutRequestView(
                    reason=reason,
                    database=self.bot.db,
                    bot=self.bot,
                    guild=ctx.guild,
                    timeout=THIRTY_MINUTES,
                    nivel=nivel,
                    user=user,
                ),
            )
        else:
            await ctx.respond("`Nivel` precisa ser menor que 4")

    @commands.slash_command(name="ban_user", description="bans a user")
    @commands.has_role(ADMIN_ROLE_ID)
    async def ban_user(
        self,
        ctx: discord.ApplicationContext,
        user: discord.User,
        reason: str,
    ) -> None:
        """."""
        if await user_check(user_id=int(user.id), context=ctx, bot=self.bot):
            return

        await ctx.response.send_message(
            content="Confirmar banimento de usuário.",
            view=BanConfirmationView(
                delete_func=ctx.delete,
                user=user,
                reason=reason,
                database=self.bot.db,
            ),
        )

    @commands.slash_command(name="unban_user", description="unbans a user")
    @commands.has_role(ADMIN_ROLE_ID)
    async def unban_user(  #! To refactor
        self,
        ctx: discord.ApplicationContext,
        reason: str,
    ) -> None:
        """."""
        guild: discord.Guild = ctx.guild
        bans: list = await guild.bans().flatten()  # BanEntry
        options: list[discord.SelectOption] = []
        banned_users: list[discord.User] = []
        for i in bans:
            banned_users.append(i.user)
            options.append(
                discord.SelectOption(
                    label=str(i.user.display_name),
                    value=str(i.user.id),
                    description=f"#{i.user.discriminator}",
                )
            )

        if len(options) > 25:
            mx_val: int = 25
        else:
            mx_val: int = len(options)

        if not bans:
            await ctx.response.send_message(content="Não existem usuários banidos.")
        else:
            await ctx.response.send_message(
                content="Selecione o usuário para desbanir",
                view=UserUnbanView(
                    delete_func=ctx.delete,
                    reason=reason,
                    database=self.bot.db,
                    options=options,
                    max_val=mx_val,
                    bans=banned_users,
                ),
            )

    @commands.slash_command(name="lock", description="locks the server in case of raid")
    @commands.has_role(ADMIN_ROLE_ID)
    async def lock(self, ctx: discord.ApplicationContext) -> None:  #! To refactor
        """."""
        guild: discord.Guild = ctx.guild
        user: discord.User = ctx.user
        database: CustomDatabase = self.bot.db
        for category in guild.categories:
            if category.name.lower() == "server_lock":
                is_server_lock: bool = True
                lock_category: discord.CategoryChannel = category
                break
        else:
            is_server_lock: bool = False

        if not is_server_lock:
            curr_unix_time: int = int(time())
            embed: discord.Embed = discord.Embed(
                title="Alerta de invasão (raid)",
                description=f"Um dos moderadores ({user.mention}) detectou uma invasão",
                color=discord.Colour.red(),
                timestamp=datetime.now(),
            )
            embed.add_field(
                name="Status do servidor.",
                value=f"""O servidor atualmente se encontra em **LOCK MODE**.
            Todos os canais e dados foram salvos e só podem ser restaurados pelo dono do servidor ({guild.owner.mention}).
            Até que essa situação se resolva vocês serão notificados através deste canal.""",
                inline=False,
            )
            embed.set_author(name="Frontless Programming", icon_url=BOT_ICON_URL)
            embed.set_footer(
                text="Atenciosamente, FrontlessTeam.", icon_url=BOT_ICON_URL
            )

            sec_perms: discord.PermissionOverwrite = discord.PermissionOverwrite(
                view_channel=True,
                connect=True,
                send_messages=True,
                speak=True,
                read_messages=True,
                send_messages_in_threads=True,
            )
            ever_perms: discord.PermissionOverwrite = discord.PermissionOverwrite(
                connect=False,
                send_messages=False,
                speak=False,
                send_tts_messages=False,
                send_messages_in_threads=False,
                start_embedded_activities=False,
                add_reactions=False,
                view_channel=False,
            )
            ever_status_perms: discord.PermissionOverwrite = (
                discord.PermissionOverwrite(
                    connect=True,
                    read_messages=True,
                    send_messages=False,
                    speak=False,
                    send_tts_messages=False,
                    send_messages_in_threads=False,
                    start_embedded_activities=False,
                    add_reactions=False,
                    view_channel=True,
                )
            )
            roles_list: list[discord.Role] = guild.roles
            chan_list: list[
                discord.VoiceChannel
                | discord.StageChannel
                | discord.TextChannel
                | discord.ForumChannel
                | discord.CategoryChannel
            ] = guild.channels
            await ctx.response.send_message(content="Trancando servidor.")

            await database.lock_state_func(
                roles=roles_list, channels=chan_list, curr_unix_time=curr_unix_time
            )

            for role in roles_list:
                for chan in chan_list:
                    print(f"Settings permissions for role: {role} on channel: {chan}.")
                    await chan.set_permissions(target=role, overwrite=ever_perms)
            print("DONE.")

            lock_category: discord.CategoryChannel = await guild.create_category(
                name="server_lock"
            )
            bot_usr_obj: discord.Member = guild.get_member(self.bot.user.id)
            guild_owner_obj: discord.Member = guild.owner
            for i in guild.roles:
                await lock_category.set_permissions(
                    target=i, overwrite=ever_status_perms
                )
            await lock_category.set_permissions(target=bot_usr_obj, overwrite=sec_perms)
            await lock_category.set_permissions(
                target=guild_owner_obj, overwrite=sec_perms
            )
            lock_text_chan: discord.TextChannel = (
                await lock_category.create_text_channel(name="status_text_channel")
            )
            await lock_category.create_voice_channel(name="status_voice_channel")
            await lock_category.move(beginning=True)
            await lock_text_chan.send(embed=embed)
        else:
            await ctx.response.send_message(content="Server já trancado.")

    @commands.slash_command(name="restore", description="restore the server lock")
    @commands.is_owner()
    async def restore(self, ctx: discord.ApplicationContext) -> None:  #! To refactor
        """."""
        guild: discord.Guild = ctx.guild
        database: CustomDatabase = self.bot.db
        final_permissions_result_dict: dict[str, bool] = {}
        for category in guild.categories:
            if category.name.lower() == "server_lock":
                print(category.name.lower())
                is_server_lock: bool = True
                lock_category: discord.CategoryChannel = category
                break
        else:
            is_server_lock: bool = False

        if is_server_lock:
            await ctx.response.send_message(content="Restaurando servidor.")
            permissions_dict: dict[str, int] = discord.Permissions.VALID_FLAGS
            state = await database.fetch(table="lock_state")
            for item in state:
                channel: discord.TextChannel = guild.get_channel(int(item[1]))
                role: discord.Role = guild.get_role(int(item[0]))
                permssions_int: discord.Permissions = discord.Permissions(int(item[2]))
                for _k, _v in permissions_dict.items():
                    final_permissions_result_dict[_k] = bool(
                        (int(permssions_int.value) & int(_v)) == int(_v)
                    )

                permissions_final: discord.PermissionOverwrite = (
                    discord.PermissionOverwrite(**final_permissions_result_dict)
                )
                print(f"Restoring permissions for role {role} on channel {channel}.")
                await channel.set_permissions(target=role, overwrite=permissions_final)
            print("DONE")

            for item in state:
                channel: discord.TextChannel = guild.get_channel(int(item[1]))
                if not channel.permissions_synced:
                    print(f"Synchronizing permissions for channel {channel.name}")
                    await channel.edit(sync_permissions=True)
                    print(f"Setting 5 seconds slowmode for channel {channel.name}")
                    await channel.edit(slowmode_delay=5)
            print("DONE")

            for chan_ in lock_category.channels:
                await chan_.delete()
            await lock_category.delete()
            await database.clear_table("lock_state")

        else:
            await ctx.response.send_message(content="Servidor não trancado.")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Listener para reativar os botões ao iniciar do bot"""

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """."""
        base_err_msg: str = (
            f"Permissão negada {ctx.author.name} esse comando só pode ser usado"
        )
        if isinstance(error, commands.MissingRole):
            await ctx.send(
                content=f"{base_err_msg} por um administrador.",
                reference=ctx.message,
                delete_after=4,
            )
        elif isinstance(error, commands.NotOwner):
            await ctx.send(
                content=f"{base_err_msg} pelo dono do servidor.",
                reference=ctx.message,
                delete_after=4,
            )
        else:
            await ctx.send(
                "Um erro inesperado ocorreu.",
                reference=ctx.message,
                delete_after=4,
            )
            raise error


def setup(bot) -> None:
    """Function that sets up the cog for the bot"""
    bot.add_cog(Adminstrative(bot))
