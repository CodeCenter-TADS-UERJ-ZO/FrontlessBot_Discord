"""Módulo do bot que contém toda a funcionalidade de administração"""
# pylint: disable=line-too-long too-many-lines too-many-locals too-many-branches too-many-statements too-many-instance-attributes too-many-arguments

import typing
from datetime import datetime, timedelta
from time import time
from aiosqlite import Connection
import discord
from discord.ext import commands

timeout_types: dict[str, list[typing.Union[int, str]]] = {
    "1": [60, "1 minuto"],
    "2": [300, "5 minutos"],
    "3": [600, "10 minutos"],
    "4": [3600, "1 hora"],
    "5": [86400, "1 dia"],
    "6": [604800, "1 semana"],
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

bot_icon_url: str = "https://cdn.discordapp.com/app-icons/1056943227183321118/08902aef3ee87acc3e69081c0a012b71.png?size=2048"  # pylint: disable=line-too-long
mod_logs_chan_id: int = 1059634018653585470


# ██████████████████████████████████████████████████████████████████████████████████████████████████████████╗
# ╚═════════════════════════════════════════════════════════════════════════════════════════════════════════╝

# ██╗  ██╗███████╗██╗     ██████╗ ███████╗██████╗     ███████╗██╗   ██╗███╗   ██╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗███████╗
# ██║  ██║██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗    ██╔════╝██║   ██║████╗  ██║██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║██╔════╝
# ███████║█████╗  ██║     ██████╔╝█████╗  ██████╔╝    █████╗  ██║   ██║██╔██╗ ██║██║        ██║   ██║██║   ██║██╔██╗ ██║███████╗
# ██╔══██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══██╗    ██╔══╝  ██║   ██║██║╚██╗██║██║        ██║   ██║██║   ██║██║╚██╗██║╚════██║
# ██║  ██║███████╗███████╗██║     ███████╗██║  ██║    ██║     ╚██████╔╝██║ ╚████║╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║███████║
# ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝    ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝

# ██████████████████████████████████████████████████████████████████████████████████████████████████████████╗
# ╚═════════════════════════════════════════════════════════════════════════════════════════════════════════╝


def hex_to_rgb(hex_code: str) -> tuple[str]:
    """return a tuple with the rgb values of a hex color"""
    _h: str = hex_code.lstrip("#")
    return tuple(int(_h[i : i + 2], 16) for i in (0, 2, 4))


# ██████████████████████████████████████████████████████████████████████████████████████████████████████████╗
# ╚═════════════════════════════════════════════════════════════════════════════════════════════════════════╝

#  ██████╗ ██╗       █████╗  ███████╗ ███████╗ ███████╗ ███████╗
# ██╔════╝ ██║      ██╔══██╗ ██╔════╝ ██╔════╝ ██╔════╝ ██╔════╝
# ██║      ██║      ███████║ ███████╗ ███████╗ █████╗   ███████╗
# ██║      ██║      ██╔══██║ ╚════██║ ╚════██║ ██╔══╝   ╚════██║
# ╚██████╗ ███████╗ ██║  ██║ ███████║ ███████║ ███████╗ ███████║
#  ╚═════╝ ╚══════╝ ╚═╝  ╚═╝ ╚══════╝ ╚══════╝ ╚══════╝ ╚══════╝

# ██████████████████████████████████████████████████████████████████████████████████████████████████████████╗
# ╚═════════════════════════════════════════════════════════════════════════════════════════════════════════╝

# ████████╗██╗███╗   ███╗███████╗ ██████╗ ██╗   ██╗████████╗    ██╗   ██╗██╗███████╗██╗    ██╗
# ╚══██╔══╝██║████╗ ████║██╔════╝██╔═══██╗██║   ██║╚══██╔══╝    ██║   ██║██║██╔════╝██║    ██║
#    ██║   ██║██╔████╔██║█████╗  ██║   ██║██║   ██║   ██║       ██║   ██║██║█████╗  ██║ █╗ ██║
#    ██║   ██║██║╚██╔╝██║██╔══╝  ██║   ██║██║   ██║   ██║       ╚██╗ ██╔╝██║██╔══╝  ██║███╗██║
#    ██║   ██║██║ ╚═╝ ██║███████╗╚██████╔╝╚██████╔╝   ██║        ╚████╔╝ ██║███████╗╚███╔███╔╝
#    ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚═════╝    ╚═╝         ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝


class TimeOutDropdownMenuView(discord.ui.View):
    """."""

    def __init__(  # pylint: disable=useless-parent-delegation
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        user: discord.User,
        delete_func,
        delete_parent_msg_func,
        reason: str,
        database: Connection,
        bot_event_wait_func: typing.Any,
        delete_cmd_msg=None,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.user: discord.User = user
        self.delete_func: typing.Any = delete_func
        self.delete_parent_msg_func: typing.Any = delete_parent_msg_func
        self.reason: str = reason
        self.database: Connection = database
        self.bot_event_wait_func: typing.Any = bot_event_wait_func
        self.delete_cmd_msg = delete_cmd_msg

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
            mod_logs_chan_id
        )

        selected_value: typing.Any = selection.values[0]
        if selected_value in timeout_types:
            self.stop()
            timeout_time: int = int(timeout_types[selected_value][0])  # type: ignore
            timeout_description: str = str(timeout_types[selected_value][1])  # type: ignore
            await self.user.timeout_for(timedelta(seconds=timeout_time))  # type: ignore
            timeout_embed: discord.Embed = discord.Embed(
                title="Aviso de timeout",
                description=f"Timeout de {timeout_description} aplicado ao usuário {self.user.mention} pelo moderador {interaction.user.mention}.",
                colour=discord.Colour.orange(),
                timestamp=datetime.now(),
            )
            timeout_embed.set_thumbnail(url=self.user.avatar.url)

            await mod_log_chan.send(embed=timeout_embed)
            await interaction.response.send_message(
                content=f"aplicando timeout de {timeout_description} ao usuário {self.user.mention}",
                ephemeral=True,
            )
            await interaction.delete_original_response(delay=2)
            if self.delete_func is not None:
                await self.delete_func(delay=1)
            if self.delete_parent_msg_func is not None:
                await self.delete_parent_msg_func(delay=1)

            timeout_type: str = "moderation"
            await self.bot_event_wait_func()
            async with self.database.cursor() as cursor:
                exec_cmd: str = "INSERT OR IGNORE INTO active_timeouts(user_name, user_discriminator, user_id, timeout_description, reason, level, type, unix_date) VALUES(?,?,?,?,?,?,?,?)"
                exec_cmd2: str = "INSERT OR IGNORE INTO timeouts_history(user_name, user_discriminator, user_id, timeout_description, reason, level, type, unix_date) VALUES(?,?,?,?,?,?,?,?)"
                await cursor.execute(
                    exec_cmd,
                    (
                        self.user.name,
                        self.user.discriminator,
                        int(self.user.id),
                        timeout_description,
                        str(self.reason),
                        int(selected_value),
                        timeout_type,
                        int(time()),
                    ),
                )
                await cursor.execute(
                    exec_cmd2,
                    (
                        self.user.name,
                        self.user.discriminator,
                        int(self.user.id),
                        timeout_description,
                        str(self.reason),
                        int(selected_value),
                        timeout_type,
                        int(time()),
                    ),
                )
            await self.database.commit()
        elif selected_value == "0":
            self.stop()
            await interaction.response.send_message(
                "Ignorando violação de diretrizes.", ephemeral=True
            )
            await interaction.delete_original_response(delay=2)
            if self.delete_func is not None:
                await self.delete_func(delay=1)
            if self.delete_parent_msg_func is not None:
                await self.delete_parent_msg_func(delay=1)
            if self.delete_cmd_msg is not None:
                self.delete_cmd_msg(delete_after=1)
        else:
            self.stop()
            await self.bot_event_wait_func()
            async with self.database.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM timeouts WHERE user_id=?", (self.user.id,)
                )
                user_timeout: typing.Any = await cursor.fetchall()
                user_timeout_types: list[int] = []
                for i in user_timeout:
                    user_timeout_types.append(i[3])

                max_timeout_types: int = int(max(timeout_types.keys()))
                if user_timeout == []:
                    max_user_timeout_type = 0
                else:
                    max_user_timeout_type: int = int(max(user_timeout_types))

                if max_user_timeout_type == max_timeout_types:
                    timeout_time: int = int(timeout_types[str(max_timeout_types)][0])
                    timeout_description: str = str(
                        timeout_types[str(max_timeout_types)][1]
                    )
                    await interaction.response.send_message(
                        content=f"Usuário já contém um timeout de {timeout_description}, diretrizes implicam que a próxima medida preventiva seja banimento, deseja aplica-lo?",
                        view=BanConfirmationView(
                            user=self.user,
                            delete_func=self.delete_func,
                            database=self.database,
                            bot_event_wait_func=self.bot_event_wait_func,
                            reason=self.reason,
                        ),
                    )
                else:
                    max_user_timeout_type += 1
                    timeout_time: int = int(
                        timeout_types[str(max_user_timeout_type)][0]
                    )
                    timeout_description: str = str(
                        timeout_types[str(max_user_timeout_type)][1]
                    )

                    await self.user.timeout_for(timedelta(seconds=timeout_time))  # type: ignore
                    await interaction.response.send_message(
                        content=f"aplicando timeout de {timeout_description} ao usuário {self.user.mention}",
                        ephemeral=True,
                    )
                    timeout_embed: discord.Embed = discord.Embed(
                        title="Aviso de timeout",
                        description=f"Timeout de {timeout_description} aplicado ao usuário {self.user.mention} pelo moderador {interaction.user.mention}.",
                        colour=discord.Colour.orange(),
                        timestamp=datetime.now(),
                    )
                    timeout_embed.set_thumbnail(url=self.user.avatar.url)

                    await mod_log_chan.send(embed=timeout_embed)
                    await interaction.delete_original_response(delay=2)
                    if self.delete_func is not None:
                        await self.delete_func(delay=1)
                    if self.delete_parent_msg_func is not None:
                        await self.delete_parent_msg_func(delay=1)

                    timeout_type: str = "moderation"
                    await self.bot_event_wait_func()
                    async with self.database.cursor() as cursor:
                        exec_cmd: str = "INSERT OR IGNORE INTO active_timeouts(user_name, user_discriminator, user_id, timeout_description, reason, level, type, unix_date) VALUES(?,?,?,?,?,?,?,?)"
                        exec_cmd2: str = "INSERT OR IGNORE INTO timeouts_history(user_name, user_discriminator, user_id, timeout_description, reason, level, type, unix_date) VALUES(?,?,?,?,?,?,?,?)"
                        await cursor.execute(
                            exec_cmd,
                            (
                                self.user.name,
                                self.user.discriminator,
                                int(self.user.id),
                                timeout_description,
                                str(self.reason),
                                int(selected_value),
                                timeout_type,
                                int(time()),
                            ),
                        )
                        await cursor.execute(
                            exec_cmd2,
                            (
                                self.user.name,
                                self.user.discriminator,
                                int(self.user.id),
                                timeout_description,
                                str(self.reason),
                                int(selected_value),
                                timeout_type,
                                int(time()),
                            ),
                        )
                    await self.database.commit()


# ████████╗██╗███╗   ███╗███████╗ ██████╗ ██╗   ██╗████████╗    ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ████████╗
# ╚══██╔══╝██║████╗ ████║██╔════╝██╔═══██╗██║   ██║╚══██╔══╝    ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝
#    ██║   ██║██╔████╔██║█████╗  ██║   ██║██║   ██║   ██║       ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝   ██║
#    ██║   ██║██║╚██╔╝██║██╔══╝  ██║   ██║██║   ██║   ██║       ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝    ██║
#    ██║   ██║██║ ╚═╝ ██║███████╗╚██████╔╝╚██████╔╝   ██║       ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║        ██║
#    ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚═════╝    ╚═╝       ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝


class TimeOutPromptView(discord.ui.View):
    """."""

    def __init__(  # pylint: disable=useless-parent-delegation
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        user: discord.User | discord.Member,
        delete_func,
        reason: str,
        database: Connection,
        bot_event_wait_func: typing.Any,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.user: discord.User = user
        self.delete_func: typing.Any = delete_func
        self.reason: str = reason
        self.database: Connection = database
        self.bot_event_wait_func = bot_event_wait_func

    @discord.ui.button(
        label="Sim", style=discord.ButtonStyle.primary, custom_id="ybtn_tmout"
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
                bot_event_wait_func=self.bot_event_wait_func,
            ),
        )

    @discord.ui.button(
        label="Não", style=discord.ButtonStyle.danger, custom_id="nbtn_tmout"
    )
    async def no_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        self.stop()
        await interaction.response.send_message("Ignorando violação de diretrizes.")
        await interaction.delete_original_response(delay=3)
        await self.delete_func(delay=1)


# ██████╗  ██████╗ ██╗     ███████╗    ███████╗███████╗██╗     ███████╗ ██████╗████████╗
# ██╔══██╗██╔═══██╗██║     ██╔════╝    ██╔════╝██╔════╝██║     ██╔════╝██╔════╝╚══██╔══╝
# ██████╔╝██║   ██║██║     █████╗      ███████╗█████╗  ██║     █████╗  ██║        ██║
# ██╔══██╗██║   ██║██║     ██╔══╝      ╚════██║██╔══╝  ██║     ██╔══╝  ██║        ██║
# ██║  ██║╚██████╔╝███████╗███████╗    ███████║███████╗███████╗███████╗╚██████╗   ██║
# ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝    ╚══════╝╚══════╝╚══════╝╚══════╝ ╚═════╝   ╚═╝


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

    async def callback(  # pylint: disable=too-many-locals too-many-branches
        self, interaction: discord.Interaction
    ) -> None:
        """."""
        if self.values[0] != "None":
            message: discord.Message = interaction.message  # type: ignore
            guild: discord.Guild = interaction.guild  # type: ignore
            user: discord.Member = interaction.user  # type: ignore
            dev_role: discord.Role = guild.get_role(1058049513111167016)  # type: ignore
            selected_roles: list[discord.Role] = []
            roles_to_add: list[discord.Role] = []
            roles_to_remove: list[discord.Role] = []
            roles_to_add_mentions: list[str] = []
            roles_to_remove_mentions: list[str] = []

            for i in self.values:
                role: discord.Role = guild.get_role(int(i))  # type: ignore
                selected_roles.append(role)

            for _role in selected_roles:
                if _role not in user.roles:
                    roles_to_add.append(_role)
                    roles_to_add_mentions.append(_role.mention)
                else:
                    roles_to_remove.append(_role)
                    roles_to_remove_mentions.append(_role.mention)

            if dev_role in user.roles:
                for _role_add in roles_to_add:
                    await user.add_roles(_role_add)

                for _role_remove in roles_to_remove:
                    await user.remove_roles(_role_remove)

                adding_str: str = (
                    f"adicionando cargos: {', '.join(roles_to_add_mentions)}"
                )
                removing_str: str = (
                    f"removendo cargos: {', '.join(roles_to_remove_mentions)}"
                )
                if len(selected_roles) == 0:
                    message_content: str = "Selecione algum cargo"
                else:
                    if len(roles_to_remove_mentions) == 0:
                        message_content: str = adding_str.capitalize()
                    elif len(roles_to_add_mentions) == 0:
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
                    ephemeral=True,  # type: ignore
                    delete_after=5,
                )
        else:
            await interaction.response.send_message(
                content="Não há cargos a serem adicionados.",
                ephemeral=True,
                delete_after=5,
            )


# ██████╗ ███████╗██████╗ ███████╗██╗███████╗████████╗███████╗███╗   ██╗████████╗    ██╗   ██╗██╗███████╗██╗    ██╗
# ██╔══██╗██╔════╝██╔══██╗██╔════╝██║██╔════╝╚══██╔══╝██╔════╝████╗  ██║╚══██╔══╝    ██║   ██║██║██╔════╝██║    ██║
# ██████╔╝█████╗  ██████╔╝███████╗██║███████╗   ██║   █████╗  ██╔██╗ ██║   ██║       ██║   ██║██║█████╗  ██║ █╗ ██║
# ██╔═══╝ ██╔══╝  ██╔══██╗╚════██║██║╚════██║   ██║   ██╔══╝  ██║╚██╗██║   ██║       ╚██╗ ██╔╝██║██╔══╝  ██║███╗██║
# ██║     ███████╗██║  ██║███████║██║███████║   ██║   ███████╗██║ ╚████║   ██║        ╚████╔╝ ██║███████╗╚███╔███╔╝
# ╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═══╝   ╚═╝         ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝


class PersistentView(discord.ui.View):
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


#  ██████╗ ██████╗ ██████╗ ███████╗    ██████╗  ██████╗ ██╗     ███████╗    ███╗   ███╗ ██████╗ ██████╗  █████╗ ██╗
# ██╔════╝██╔═══██╗██╔══██╗██╔════╝    ██╔══██╗██╔═══██╗██║     ██╔════╝    ████╗ ████║██╔═══██╗██╔══██╗██╔══██╗██║
# ██║     ██║   ██║██║  ██║█████╗      ██████╔╝██║   ██║██║     █████╗      ██╔████╔██║██║   ██║██║  ██║███████║██║
# ██║     ██║   ██║██║  ██║██╔══╝      ██╔══██╗██║   ██║██║     ██╔══╝      ██║╚██╔╝██║██║   ██║██║  ██║██╔══██║██║
# ╚██████╗╚██████╔╝██████╔╝███████╗    ██║  ██║╚██████╔╝███████╗███████╗    ██║ ╚═╝ ██║╚██████╔╝██████╔╝██║  ██║███████╗
#  ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝    ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝


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


# ██████╗  █████╗ ███╗   ██╗     ██████╗ ██████╗ ███╗   ██╗███████╗██╗██████╗ ███╗   ███╗    ██╗   ██╗██╗███████╗██╗    ██╗
# ██╔══██╗██╔══██╗████╗  ██║    ██╔════╝██╔═══██╗████╗  ██║██╔════╝██║██╔══██╗████╗ ████║    ██║   ██║██║██╔════╝██║    ██║
# ██████╔╝███████║██╔██╗ ██║    ██║     ██║   ██║██╔██╗ ██║█████╗  ██║██████╔╝██╔████╔██║    ██║   ██║██║█████╗  ██║ █╗ ██║
# ██╔══██╗██╔══██║██║╚██╗██║    ██║     ██║   ██║██║╚██╗██║██╔══╝  ██║██╔══██╗██║╚██╔╝██║    ╚██╗ ██╔╝██║██╔══╝  ██║███╗██║
# ██████╔╝██║  ██║██║ ╚████║    ╚██████╗╚██████╔╝██║ ╚████║██║     ██║██║  ██║██║ ╚═╝ ██║     ╚████╔╝ ██║███████╗╚███╔███╔╝
# ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝     ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝      ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝


class BanConfirmationView(discord.ui.View):
    """."""

    def __init__(  # pylint: disable=useless-parent-delegation
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        user: discord.User,
        delete_func,
        reason: str,
        database: Connection,
        bot_event_wait_func: typing.Any,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.user: discord.User = user
        self.delete_func: typing.Any = delete_func
        self.reason: str = reason
        self.database: Connection = database
        self.bot_event_wait_func = bot_event_wait_func

    @discord.ui.button(
        label="Sim", style=discord.ButtonStyle.primary, custom_id="ybtn_tmout"
    )
    async def yes_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        self.stop()
        mod_log_chan: discord.TextChannel = interaction.guild.get_channel(
            mod_logs_chan_id
        )
        timeout_embed: discord.Embed = discord.Embed(
            title="Aviso de banimento",
            description=f"Banimento aplicado ao usuário {self.user.mention} pelo moderador {interaction.user.mention}.",
            colour=discord.Colour.red(),
            timestamp=datetime.now(),
        )
        timeout_embed.set_thumbnail(url=self.user.avatar.url)

        await mod_log_chan.send(embed=timeout_embed)
        await interaction.response.send_message(
            content=f"Banindo {self.user.mention}.", ephemeral=True
        )
        epoch_date: int = int(time())
        await self.bot_event_wait_func()
        async with self.database.cursor() as cursor:
            add_act_ban_command: str = "INSERT OR IGNORE INTO active_bans(user_name, user_discriminator, user_id, reason, unix_date) VALUES(?,?,?,?,?)"
            add_hist_ban_command: str = "INSERT OR IGNORE INTO ban_history(user_name, user_discriminator, user_id, reason, unix_date) VALUES(?,?,?,?,?)"
            await cursor.execute(
                add_act_ban_command,
                (
                    str(self.user.name),
                    str(self.user.discriminator),
                    int(self.user.id),
                    self.reason,
                    epoch_date,
                ),
            )
            await cursor.execute(
                add_hist_ban_command,
                (
                    str(self.user.name),
                    str(self.user.discriminator),
                    int(self.user.id),
                    self.reason,
                    epoch_date,
                ),
            )
        await self.database.commit()
        await self.user.ban(reason=self.reason)
        await interaction.delete_original_response(delay=3)
        await self.delete_func(delay=1)

    @discord.ui.button(
        label="Não", style=discord.ButtonStyle.danger, custom_id="nbtn_tmout"
    )
    async def no_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        self.stop()
        await interaction.response.send_message("Ignorando violação de diretrizes.")
        await interaction.delete_original_response(delay=3)
        await self.delete_func(delay=1)


# ██╗   ██╗███╗   ██╗██████╗  █████╗ ███╗   ██╗    ██████╗ ██████╗  ██████╗ ██████╗ ██████╗  ██████╗ ██╗    ██╗███╗   ██╗
# ██║   ██║████╗  ██║██╔══██╗██╔══██╗████╗  ██║    ██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔═══██╗██║    ██║████╗  ██║
# ██║   ██║██╔██╗ ██║██████╔╝███████║██╔██╗ ██║    ██║  ██║██████╔╝██║   ██║██████╔╝██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║
# ██║   ██║██║╚██╗██║██╔══██╗██╔══██║██║╚██╗██║    ██║  ██║██╔══██╗██║   ██║██╔═══╝ ██║  ██║██║   ██║██║███╗██║██║╚██╗██║
# ╚██████╔╝██║ ╚████║██████╔╝██║  ██║██║ ╚████║    ██████╔╝██║  ██║╚██████╔╝██║     ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║
#  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝


class UserUnbanDropdown(discord.ui.Select):
    """."""

    def __init__(
        self,
        options: list[discord.SelectOption],
        max_val: int,
        delete_func,
        reason: str,
        database: Connection,
        bot_event_wait_func: typing.Any,
        bans: typing.Any,
    ) -> None:
        super().__init__(
            placeholder="Selecione o usuário.",
            max_values=max_val,
            min_values=0,
            options=options,
        )
        self.delete_func: typing.Any = delete_func
        self.reason: str = reason
        self.database: Connection = database
        self.bot_event_wait_func: typing.Any = bot_event_wait_func
        self.bans: list[discord.User] = bans

    async def callback(  # pylint: disable=too-many-locals too-many-branches
        self, interaction: discord.Interaction
    ) -> None:
        """."""
        welcome_channel: discord.TextChannel = interaction.guild.get_channel(
            1056710866147483760
        )
        invite: discord.Invite = await welcome_channel.create_invite(
            max_uses=1, max_age=172800
        )
        for i in self.bans:
            if int(self.values[0]) == i.id:
                unban_user: discord.User = i

        mod_log_chan: discord.TextChannel = interaction.guild.get_channel(
            mod_logs_chan_id
        )
        timeout_embed: discord.Embed = discord.Embed(
            title="Aviso da moderação",
            description=f"Banimento do usuário {unban_user.mention} revogado pelo moderador {interaction.user.mention}.",
            colour=discord.Colour.darker_grey(),
            timestamp=datetime.now(),
        )
        timeout_embed.set_thumbnail(url=unban_user.avatar.url)

        await mod_log_chan.send(embed=timeout_embed)
        await interaction.guild.unban(user=unban_user)
        await interaction.response.send_message(
            f"Ban do usuário {unban_user.mention} revogado."
        )
        await unban_user.send(
            f"Seu ban no Frontless Programming foi revogado, para voltar ao servidor acesse o este link: {invite.url}, ele ficará disponível por 48 horas."
        )
        await self.bot_event_wait_func()
        async with self.database.cursor() as cursor:
            del_cmd: str = "DELETE FROM active_bans WHERE user_id=?"
            await cursor.execute(del_cmd, (unban_user.id,))
        await self.database.commit()


# ██╗   ██╗███╗   ██╗██████╗  █████╗ ███╗   ██╗    ██╗   ██╗██╗███████╗██╗    ██╗
# ██║   ██║████╗  ██║██╔══██╗██╔══██╗████╗  ██║    ██║   ██║██║██╔════╝██║    ██║
# ██║   ██║██╔██╗ ██║██████╔╝███████║██╔██╗ ██║    ██║   ██║██║█████╗  ██║ █╗ ██║
# ██║   ██║██║╚██╗██║██╔══██╗██╔══██║██║╚██╗██║    ╚██╗ ██╔╝██║██╔══╝  ██║███╗██║
# ╚██████╔╝██║ ╚████║██████╔╝██║  ██║██║ ╚████║     ╚████╔╝ ██║███████╗╚███╔███╔╝
#  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝      ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝


class UserUnbanView(discord.ui.View):
    """."""

    def __init__(
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        delete_func,
        reason: str,
        database: Connection,
        bot_event_wait_func: typing.Any,
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
                bot_event_wait_func=bot_event_wait_func,
                delete_func=delete_func,
                reason=reason,
                bans=bans,
            )
        )


# ██╗    ██╗ █████╗ ██████╗ ███╗   ██╗     █████╗  ██████╗ ██████╗███████╗██████╗ ████████╗    ██╗   ██╗██╗███████╗██╗    ██╗
# ██║    ██║██╔══██╗██╔══██╗████╗  ██║    ██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗╚══██╔══╝    ██║   ██║██║██╔════╝██║    ██║
# ██║ █╗ ██║███████║██████╔╝██╔██╗ ██║    ███████║██║     ██║     █████╗  ██████╔╝   ██║       ██║   ██║██║█████╗  ██║ █╗ ██║
# ██║███╗██║██╔══██║██╔══██╗██║╚██╗██║    ██╔══██║██║     ██║     ██╔══╝  ██╔═══╝    ██║       ╚██╗ ██╔╝██║██╔══╝  ██║███╗██║
# ╚███╔███╔╝██║  ██║██║  ██║██║ ╚████║    ██║  ██║╚██████╗╚██████╗███████╗██║        ██║        ╚████╔╝ ██║███████╗╚███╔███╔╝
#  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝ ╚═════╝ ╚═════╝╚══════╝╚═╝        ╚═╝         ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝


class WarnAcceptView(discord.ui.View):
    """."""

    def __init__(
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        reason: str,
        user: discord.User,
        database: Connection,
        guild: discord.Guild,
        wait_database_function,
        bot: discord.Bot,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.reason: str = reason
        self.user: discord.User = user
        self.database: Connection = database
        self.guild: discord.Guild = guild
        self.wait_database_function = wait_database_function
        self.bot: discord.Bot = bot

    @discord.ui.button(label="Sim", style=discord.ButtonStyle.success)
    async def yes_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        user_id: int = self.user.id
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self, delete_after=60)

        if user_id == self.guild.owner_id:  # type: ignore
            await interaction.response.send_message(
                content="Dono do servidor detectado, ação cancelada.", ephemeral=True
            )
            return

        if user_id == self.bot.user.id:
            await interaction.response.send_message(
                content="FrontlessBot detectado, ação cancelada.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            content="Aplicando aviso.", ephemeral=True
        )

        await self.wait_database_function()
        async with self.database.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM active_warns WHERE user_id=?", (user_id,)
            )
            user_warn: typing.Any = await cursor.fetchall()
        if not user_warn:
            print("user not found in warn table")
            warn_type: str = "request"
            await self.wait_database_function()
            async with self.database.cursor() as cursor:
                exec_cmd: str = "INSERT OR IGNORE INTO active_warns(user_name, user_discriminator, user_id, reason, type, unix_date) VALUES(?,?,?,?,?,?)"
                exec_cmd2: str = "INSERT OR IGNORE INTO warns_history(user_name, user_discriminator, user_id, reason, type, unix_date) VALUES(?,?,?,?,?,?)"
                await cursor.execute(
                    exec_cmd,
                    (
                        self.user.name,
                        self.user.discriminator,
                        user_id,
                        self.reason,
                        warn_type,
                        int(time()),
                    ),
                )
                await cursor.execute(
                    exec_cmd2,
                    (
                        self.user.name,
                        self.user.discriminator,
                        user_id,
                        self.reason,
                        warn_type,
                        int(time()),
                    ),
                )
            await self.database.commit()
            mod_log_chan: discord.TextChannel = interaction.guild.get_channel(
                mod_logs_chan_id
            )
            timeout_embed: discord.Embed = discord.Embed(
                title="Aviso da moderação",
                description=f"{self.user.mention}, este é um aviso da moderação, a proxima sinalização será provida de um timeout.",
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


# ██╗    ██╗ █████╗ ██████╗ ███╗   ██╗    ██████╗ ███████╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗    ██╗   ██╗██╗███████╗██╗    ██╗
# ██║    ██║██╔══██╗██╔══██╗████╗  ██║    ██╔══██╗██╔════╝██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝    ██║   ██║██║██╔════╝██║    ██║
# ██║ █╗ ██║███████║██████╔╝██╔██╗ ██║    ██████╔╝█████╗  ██║   ██║██║   ██║█████╗  ███████╗   ██║       ██║   ██║██║█████╗  ██║ █╗ ██║
# ██║███╗██║██╔══██║██╔══██╗██║╚██╗██║    ██╔══██╗██╔══╝  ██║▄▄ ██║██║   ██║██╔══╝  ╚════██║   ██║       ╚██╗ ██╔╝██║██╔══╝  ██║███╗██║
# ╚███╔███╔╝██║  ██║██║  ██║██║ ╚████║    ██║  ██║███████╗╚██████╔╝╚██████╔╝███████╗███████║   ██║        ╚████╔╝ ██║███████╗╚███╔███╔╝
#  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝         ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝


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
        database: Connection,
        guild: discord.Guild,
        wait_database_function,
        bot: discord.Bot,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.reason: str = reason
        self.user: discord.User = user
        self.database: Connection = database
        self.guild: discord.Guild = guild
        self.wait_database_function = wait_database_function
        self.bot: discord.Bot = bot
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
        requests_channel: discord.TextChannel = guild.get_channel(1059280455263850577)
        for child in self.children:
            child.disabled = True

        print(f"{self.votes = }")
        if self.votes > 0:
            color: discord.Colour = discord.Colour.green()
            desc: str = "Aviso enviado a moderação."
            embed: discord.Embed = discord.Embed(
                title="Resultado", color=color, description=desc
            )
            if self.interaction_user is not None:
                accept_desc: str = f"Pedido de aviso para o usuário {self.user.mention} requisitado pelo usuário {self.interaction_user.mention}."
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

            accept_embed.set_author(name="Frontless Programming", icon_url=bot_icon_url)
            accept_embed.set_thumbnail(url=self.user.avatar.url)
            accept_embed.set_footer(
                text=(
                    f"Pedido enviado do canal {self.interaction_channel.name}, na categoria {self.interaction_channel.category.name}"
                ),
                icon_url=bot_icon_url,
            )

            await requests_channel.send(
                embed=accept_embed,
                view=WarnAcceptView(
                    reason=self.reason,
                    user=self.user,
                    database=self.database,
                    guild=self.guild,
                    wait_database_function=self.wait_database_function,
                    bot=self.bot,
                    timeout=172800,
                ),
            )
        if self.votes < 0:
            color: discord.Colour = discord.Colour.red()
            desc: str = "Aviso descartado."

            embed: discord.Embed = discord.Embed(
                title="Resultado", color=color, description=desc
            )
        elif self.votes == 0:
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
        print(f"{cls.votes = }")

    @classmethod
    def decrementer(cls) -> None:
        """."""
        cls.votes -= 1
        print(f"{cls.votes = }")

    @classmethod
    def appender(cls, user: discord.User) -> None:
        """."""
        cls.users.append(user)

    @classmethod
    def reseter(cls) -> None:
        """."""
        cls.votes = 0
        cls.users.clear()


# ████████╗██╗███╗   ███╗███████╗ ██████╗ ██╗   ██╗████████╗     █████╗  ██████╗██████╗ ████████╗    ██╗   ██╗██╗███████╗██╗    ██╗
# ╚══██╔══╝██║████╗ ████║██╔════╝██╔═══██╗██║   ██║╚══██╔══╝    ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝    ██║   ██║██║██╔════╝██║    ██║
#    ██║   ██║██╔████╔██║█████╗  ██║   ██║██║   ██║   ██║       ███████║██║     ██████╔╝   ██║       ██║   ██║██║█████╗  ██║ █╗ ██║
#    ██║   ██║██║╚██╔╝██║██╔══╝  ██║   ██║██║   ██║   ██║       ██╔══██║██║     ██╔═══╝    ██║       ╚██╗ ██╔╝██║██╔══╝  ██║███╗██║
#    ██║   ██║██║ ╚═╝ ██║███████╗╚██████╔╝╚██████╔╝   ██║       ██║  ██║╚██████╗██║        ██║██╗     ╚████╔╝ ██║███████╗╚███╔███╔╝
#    ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚═════╝    ╚═╝       ╚═╝  ╚═╝ ╚═════╝╚═╝        ╚═╝╚═╝      ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝


class TimeoutAcceptView(discord.ui.View):
    """."""

    def __init__(
        self,
        *items: discord.ui.Item,
        timeout: float | None = 180,
        disable_on_timeout: bool = False,
        reason: str,
        user: discord.User,
        database: Connection,
        guild: discord.Guild,
        wait_database_function,
        bot: discord.Bot,
        nivel: int,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.reason: str = reason
        self.user: discord.User = user
        self.database: Connection = database
        self.guild: discord.Guild = guild
        self.wait_database_function = wait_database_function
        self.bot: discord.Bot = bot
        self.nivel: int = nivel

    @discord.ui.button(label="Sim", style=discord.ButtonStyle.success)
    async def yes_button_callback(self, _, interaction: discord.Interaction) -> None:
        """."""
        user_id: int = self.user.id
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self, delete_after=60)

        if user_id == self.guild.owner_id:  # type: ignore
            await interaction.response.send_message(
                content="Dono do servidor detectado, ação cancelada.", ephemeral=True
            )
            return

        if user_id == self.bot.user.id:
            await interaction.response.send_message(
                content="FrontlessBot detectado, ação cancelada.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            content="Aplicando timeout.", ephemeral=True
        )
        timeout_description: str = timeout_types[str(self.nivel)][1]
        timeout_time: int = timeout_types[str(self.nivel)][0]
        timeout_type: str = "request"
        await self.user.timeout_for(timedelta(seconds=timeout_time))
        await self.wait_database_function()
        async with self.database.cursor() as cursor:
            exec_cmd: str = "INSERT OR IGNORE INTO active_timeouts(user_name, user_discriminator, user_id, timeout_description, reason, level, type, unix_date) VALUES(?,?,?,?,?,?,?,?)"
            exec_cmd2: str = "INSERT OR IGNORE INTO timeouts_history(user_name, user_discriminator, user_id, timeout_description, reason, level, type, unix_date) VALUES(?,?,?,?,?,?,?,?)"
            await cursor.execute(
                exec_cmd,
                (
                    self.user.name,
                    self.user.discriminator,
                    int(self.user.id),
                    timeout_description,
                    str(self.reason),
                    int(self.nivel),
                    timeout_type,
                    int(time()),
                ),
            )
            await cursor.execute(
                exec_cmd2,
                (
                    self.user.name,
                    self.user.discriminator,
                    int(self.user.id),
                    timeout_description,
                    str(self.reason),
                    int(self.nivel),
                    timeout_type,
                    int(time()),
                ),
            )
        await self.database.commit()
        mod_log_chan: discord.TextChannel = interaction.guild.get_channel(
            mod_logs_chan_id
        )
        timeout_embed: discord.Embed = discord.Embed(
            title="Aviso de timeout",
            description=f"Timeout de {timeout_description} aplicado ao usuário {self.user.mention} através de votação da comunidade.",
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


# ████████╗██╗███╗   ███╗███████╗ ██████╗ ██╗   ██╗████████╗    ██████╗ ███████╗ ██████╗        ██╗   ██╗██╗███████╗██╗    ██╗
# ╚══██╔══╝██║████╗ ████║██╔════╝██╔═══██╗██║   ██║╚══██╔══╝    ██╔══██╗██╔════╝██╔═══██╗       ██║   ██║██║██╔════╝██║    ██║
#    ██║   ██║██╔████╔██║█████╗  ██║   ██║██║   ██║   ██║       ██████╔╝█████╗  ██║   ██║       ██║   ██║██║█████╗  ██║ █╗ ██║
#    ██║   ██║██║╚██╔╝██║██╔══╝  ██║   ██║██║   ██║   ██║       ██╔══██╗██╔══╝  ██║▄▄ ██║       ╚██╗ ██╔╝██║██╔══╝  ██║███╗██║
#    ██║   ██║██║ ╚═╝ ██║███████╗╚██████╔╝╚██████╔╝   ██║       ██║  ██║███████╗╚██████╔╝██╗     ╚████╔╝ ██║███████╗╚███╔███╔╝
#    ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚═════╝    ╚═╝       ╚═╝  ╚═╝╚══════╝ ╚══▀▀═╝ ╚═╝      ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝


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
        database: Connection,
        guild: discord.Guild,
        wait_database_function,
        bot: discord.Bot,
        nivel: int,
    ) -> None:
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.reason: str = reason
        self.user: discord.User = user
        self.database: Connection = database
        self.guild: discord.Guild = guild
        self.wait_database_function = wait_database_function
        self.bot: discord.Bot = bot
        self.interaction_user = None
        self.interaction_channel = None
        self.nivel: int = nivel
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
        requests_channel: discord.TextChannel = guild.get_channel(1059280455263850577)
        for child in self.children:
            child.disabled = True

        print(f"{self.votes = }")
        if self.votes > 0:
            color: discord.Colour = discord.Colour.green()
            desc: str = "Timeout enviado a moderação."
            embed: discord.Embed = discord.Embed(
                title="Resultado", color=color, description=desc
            )
            if self.interaction_user is not None:
                accept_desc: str = f"Pedido de timeout para o usuário {self.user.mention} requisitado pelo usuário {self.interaction_user.mention}."
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

            accept_embed.set_author(name="Frontless Programming", icon_url=bot_icon_url)
            accept_embed.set_thumbnail(url=self.user.avatar.url)
            accept_embed.set_footer(
                text=(
                    f"Pedido enviado do canal {self.interaction_channel.name}, na categoria {self.interaction_channel.category.name}"
                ),
                icon_url=bot_icon_url,
            )

            await requests_channel.send(
                embed=accept_embed,
                view=TimeoutAcceptView(
                    reason=self.reason,
                    user=self.user,
                    database=self.database,
                    guild=self.guild,
                    wait_database_function=self.wait_database_function,
                    bot=self.bot,
                    timeout=172800,
                    nivel=self.nivel,
                ),
            )
        if self.votes < 0:
            color: discord.Colour = discord.Colour.red()
            desc: str = "Timeout descartado."

            embed: discord.Embed = discord.Embed(
                title="Resultado", color=color, description=desc
            )
        elif self.votes == 0:
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
        print(f"{cls.votes = }")

    @classmethod
    def decrementer(cls) -> None:
        """."""
        cls.votes -= 1
        print(f"{cls.votes = }")

    @classmethod
    def appender(cls, user: discord.User) -> None:
        """."""
        cls.users.append(user)

    @classmethod
    def reseter(cls) -> None:
        """."""
        cls.votes = 0
        cls.users.clear()


# ██████████████████████████████████████████████████████████████████████████████████████████████████████████╗
# ╚═════════════════════════════════════════════════════════════════════════════════════════════════════════╝

#  ██████╗  ██████╗   ██████╗
# ██╔════╝ ██╔═══██╗ ██╔════╝
# ██║      ██║   ██║ ██║  ███╗
# ██║      ██║   ██║ ██║   ██║
# ╚██████╗ ╚██████╔╝ ╚██████╔╝
#  ╚═════╝  ╚═════╝   ╚═════╝

# ██████████████████████████████████████████████████████████████████████████████████████████████████████████╗
# ╚═════════════════════════════════════════════════════════════════════════════════════════════════════════╝


class Adminstrative(commands.Cog):
    """Cog used to manage all Administrative commands"""

    # pylint: disable=line-too-long

    def __init__(self, bot) -> None:
        self.bot = bot
        self.bot.persistent_views_added = False

    # ██████╗ ██╗   ██╗██╗     ███████╗     ██████╗███╗   ███╗██████╗
    # ██╔══██╗██║   ██║██║     ██╔════╝    ██╔════╝████╗ ████║██╔══██╗
    # ██████╔╝██║   ██║██║     █████╗      ██║     ██╔████╔██║██║  ██║
    # ██╔══██╗██║   ██║██║     ██╔══╝      ██║     ██║╚██╔╝██║██║  ██║
    # ██║  ██║╚██████╔╝███████╗███████╗    ╚██████╗██║ ╚═╝ ██║██████╔╝
    # ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝     ╚═════╝╚═╝     ╚═╝╚═════╝

    @commands.slash_command(name="regras", description="Exibe as regras")
    @commands.has_role(1056755317419028560)
    async def regras(self, ctx: discord.ApplicationContext) -> None:
        """Função que exibe as regras do servidor"""

        await self.bot.db_connected.wait()
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM rules")
            rules: list[tuple[str, str]] = await cursor.fetchall()

        embed: discord.Embed = discord.Embed(
            title="Regras",
            description="Estas são as regras do servidor.",
            color=discord.Colour.light_grey(),
            timestamp=datetime.now(),
        )
        for _rule in rules:
            embed.add_field(name=_rule[0], value=_rule[1], inline=False)
        embed.set_author(name="Frontless Programming", icon_url=bot_icon_url)
        embed.set_thumbnail(url=bot_icon_url)
        embed.set_footer(text="Feito pela comunidade com ❤️.", icon_url=bot_icon_url)

        await ctx.respond(embed=embed)

    # ██╗      █████╗ ███╗   ██╗ ██████╗     ███████╗███████╗██╗     ███████╗ ██████╗████████╗
    # ██║     ██╔══██╗████╗  ██║██╔════╝     ██╔════╝██╔════╝██║     ██╔════╝██╔════╝╚══██╔══╝
    # ██║     ███████║██╔██╗ ██║██║  ███╗    ███████╗█████╗  ██║     █████╗  ██║        ██║
    # ██║     ██╔══██║██║╚██╗██║██║   ██║    ╚════██║██╔══╝  ██║     ██╔══╝  ██║        ██║
    # ███████╗██║  ██║██║ ╚████║╚██████╔╝    ███████║███████╗███████╗███████╗╚██████╗   ██║
    # ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝     ╚══════╝╚══════╝╚══════╝╚══════╝ ╚═════╝   ╚═╝

    @commands.slash_command(
        name="language_selection",
        description="Displays the dropdown for the language selection",
    )
    @commands.has_role(1056755317419028560)
    async def language_selection(self, ctx: discord.ApplicationContext) -> None:
        """Displays the dropdown for the language selection"""

        options: list[discord.SelectOption] = []
        await self.bot.db_connected.wait()
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM programming_languages_roles")
            roles: list[tuple[str, str, str]] = await cursor.fetchall()

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
            await ctx.edit(view=PersistentView(max_val=mx_len, options=options))
        else:
            await ctx.respond(view=PersistentView(max_val=mx_len, options=options))

    #  ██████╗██████╗ ███████╗ █████╗ ████████╗███████╗     ██████╗ █████╗ ████████╗███████╗ ██████╗  ██████╗ ██████╗ ██╗   ██╗
    # ██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔════╝    ██╔════╝██╔══██╗╚══██╔══╝██╔════╝██╔════╝ ██╔═══██╗██╔══██╗╚██╗ ██╔╝
    # ██║     ██████╔╝█████╗  ███████║   ██║   █████╗      ██║     ███████║   ██║   █████╗  ██║  ███╗██║   ██║██████╔╝ ╚████╔╝
    # ██║     ██╔══██╗██╔══╝  ██╔══██║   ██║   ██╔══╝      ██║     ██╔══██║   ██║   ██╔══╝  ██║   ██║██║   ██║██╔══██╗  ╚██╔╝
    # ╚██████╗██║  ██║███████╗██║  ██║   ██║   ███████╗    ╚██████╗██║  ██║   ██║   ███████╗╚██████╔╝╚██████╔╝██║  ██║   ██║
    #  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝     ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝

    async def _create_category_create_variables_initializer(
        self,
        ctx: discord.ApplicationContext,
        category_name: str,
        category_type: str,
        database: Connection,
        bot_event_wait_func: typing.Any,
    ) -> None:

        print("initializing variables".upper())
        guild: discord.Guild = ctx.guild  # type: ignore
        print(f"{guild = }")

        category: discord.CategoryChannel = await guild.create_category(
            name=category_name
        )
        print(f"{category = }")

        print("creating roles".upper())
        everyone_role: discord.Role = guild.get_role(1002319287308005396)  # type: ignore
        print(f"{everyone_role = }")

        if category_type.lower() == "code":
            bot_event_wait_func()
            async with database.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM github_colors WHERE name=?", (category_name.lower(),)
                )
                role_tuple: typing.Any = await cursor.fetchall()

            if role_tuple:
                role: tuple[str] = role_tuple[0]
                role_color_tuple: tuple[str] = hex_to_rgb(role[1])
                role_base: discord.Role = await guild.create_role(
                    name=role[0].capitalize(),
                    color=discord.Colour.from_rgb(
                        role_color_tuple[0], role_color_tuple[1], role_color_tuple[2]
                    ),
                )
            else:
                modal: ColorSelectorModal = ColorSelectorModal(title="Color Picker")
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
            modal_role: ProgrammingRoleDescriptionModal = (
                ProgrammingRoleDescriptionModal(title="Descrição do cargo")
            )
            await ctx.send_modal(modal_role)
            if await modal_role.wait():
                role_description: str = await modal_role.get_description()
            bot_event_wait_func()
            async with database.cursor() as cursor:
                add_role_command: str = "INSERT OR IGNORE INTO programming_languages_roles(role_id, role_name, role_description) VALUES(?,?,?)"
                await cursor.execute(
                    add_role_command,
                    (int(role_base.id), role_base.name, role_description),
                )
            await database.commit()
            print(f"{role_base = }")
            stage_adm_role: discord.Role | None = await guild.create_role(
                name=f"Adminstrador de Palcos [{role_base.name}]",
                color=discord.Colour.darker_grey(),
            )
            print(f"{stage_adm_role = }")
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
            print(f"{role_base = }")
            stage_adm_role = None
            role_base: discord.Role = await guild.create_role(name=category_name)
            print(f"{role_base = }")

        print("setting roles permissions".upper())
        everyone_permissions: discord.PermissionOverwrite = discord.PermissionOverwrite(
            view_channel=False,
            connect=False,
        )
        print(f"{everyone_permissions = }")

        role_permissions: discord.PermissionOverwrite = discord.PermissionOverwrite(
            view_channel=True,
            connect=True,
        )
        print(f"{role_permissions = }")

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
            print(f"{stage_adm_role_permissions = }")
        else:
            stage_adm_role_permissions = None

        return [
            category,
            everyone_role,
            role_base,
            stage_adm_role,
            everyone_permissions,
            role_permissions,
            stage_adm_role_permissions,
        ]  # type: ignore

    async def _create_category_set_permissions(
        self,
        category: discord.CategoryChannel,
        everyone_role: discord.Role,
        everyone_permissions: discord.PermissionOverwrite,
        role_base: discord.Role,
        role_permissions: discord.PermissionOverwrite,
        stage_adm_role: discord.Role,
        stage_adm_role_permissions: discord.PermissionOverwrite,
        category_type: str,
    ) -> None:

        print("setting permissions in category".upper())
        await category.set_permissions(
            target=everyone_role, overwrite=everyone_permissions
        )
        await category.set_permissions(target=role_base, overwrite=role_permissions)
        if category_type.lower() == "code":
            await category.set_permissions(
                target=stage_adm_role, overwrite=stage_adm_role_permissions
            )

    async def _create_category_create_voice_channels(
        self,
        ctx: discord.ApplicationContext,
        category: discord.CategoryChannel,
        role_permissions: discord.PermissionOverwrite,
        role: discord.Role,
        category_type: str,
        number_of_stage_channels: int = 2,
        number_of_voice_channels: int = 4,
        stage_channels_topic: str = "Aula Live",
        stage_channels_name: str = "Aula Live",
        voice_channels_name: str = "Estudando",
    ) -> None:
        """Helper function that creates the voice channels in the category_creator command."""

        print("creating voice channels".upper())
        await ctx.respond("Criando canais de voz")
        if category_type.lower() == "code":
            for i in range(number_of_stage_channels):
                st_chan: discord.StageChannel = await category.create_stage_channel(
                    name=f"{stage_channels_name} {i+1:0>2}", topic=stage_channels_topic
                )
                await st_chan.set_permissions(target=role, overwrite=role_permissions)
                print(f"{st_chan = }")

            for i in range(number_of_voice_channels):
                await category.create_voice_channel(
                    name=f"{voice_channels_name} {i+1:0>2}"
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
                await squad_vc.edit(user_limit=2)
            for i in range(4):
                await category.create_voice_channel(name=f"Livre {i+1:0>2}")

    async def _create_category_create_text_channels(
        self,
        ctx: discord.ApplicationContext,
        category: discord.CategoryChannel,
        category_type: str,
    ) -> None:
        """Helper function that creates the voice channels in the category_creator command."""
        print("creating text channels".upper())
        await ctx.respond("Criando canais de texto")

        w_chan: discord.TextChannel = await category.create_text_channel(
            name="boas-vindas"
        )
        print(f"{w_chan = }")

        r_chan: discord.TextChannel = await category.create_text_channel(name="regras")
        print(f"{r_chan = }")

        g_chan: discord.TextChannel = await category.create_text_channel(name="geral")
        print(f"{g_chan = }")
        await w_chan.move(beginning=True)
        await r_chan.move(after=w_chan)
        await g_chan.move(after=r_chan)

        await w_chan.edit(slowmode_delay=10)
        await r_chan.edit(slowmode_delay=10)
        await g_chan.edit(slowmode_delay=10)

        if category_type.lower() == "code":
            s_chan: discord.ForumChannel = await category.create_forum_channel(
                name="suporte"
            )
            print(f"{s_chan = }")
            await s_chan.move(after=g_chan)
            await s_chan.edit(slowmode_delay=5)

    @commands.slash_command(
        name="create_category",
        description="Cria uma categoria, os cargos e configura todos os canais",
    )
    @commands.has_role(1056755317419028560)
    async def create_category(
        self, ctx: discord.ApplicationContext, name: str, category_type: str
    ) -> None:
        """Comando de gerenciamento de categorias, especifico para as categorias de linguagem
        tem como argumento o nome da linguagem em questão e cria todos os canais base da categoria
        além de criar o cargo e configurar as permissões."""

        if category_type not in ["code", "game"]:
            await ctx.response.send_message("Tipo da categoria não reconhecido.")
            return

        [
            category,
            everyone_role,
            role_base,
            stage_adm_role,
            everyone_permissions,
            role_permissions,
            stage_adm_role_permissions,
        ] = await self._create_category_create_variables_initializer(
            ctx=ctx,
            category_name=name,
            category_type=category_type,
            database=self.bot.db,
            bot_event_wait_func=self.bot.db_connected.wait,
        )  # type: ignore

        await self._create_category_set_permissions(
            category=category,
            everyone_role=everyone_role,
            everyone_permissions=everyone_permissions,
            role_base=role_base,
            role_permissions=role_permissions,
            stage_adm_role=stage_adm_role,
            stage_adm_role_permissions=stage_adm_role_permissions,
            category_type=category_type,
        )

        await self._create_category_create_text_channels(
            ctx=ctx, category=category, category_type=category_type
        )
        await self._create_category_create_voice_channels(
            ctx=ctx,
            category=category,
            role=stage_adm_role,
            role_permissions=stage_adm_role_permissions,
            category_type=category_type,
        )

        for chan in category.channels:
            if not chan.permissions_synced:
                await chan.edit(sync_permissions=True)

        print("done".upper())
        await ctx.respond(
            f"Categoria {category.name}, {role_base.mention} e {stage_adm_role.mention} criados",
        )

    # ██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗     ██████╗███╗   ███╗██████╗
    # ██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝    ██╔════╝████╗ ████║██╔══██╗
    # ██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗      ██║     ██╔████╔██║██║  ██║
    # ██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝      ██║     ██║╚██╔╝██║██║  ██║
    # ╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗    ╚██████╗██║ ╚═╝ ██║██████╔╝
    #  ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝     ╚═════╝╚═╝     ╚═╝╚═════╝

    @commands.slash_command(name="welcome", description="Exibe a tela de boas-vindas")
    @commands.has_role(1056755317419028560)
    async def welcome(self, ctx: discord.ApplicationContext) -> None:
        """."""

        guild: discord.Guild = ctx.guild  # type: ignore
        rule_channel: discord.TextChannel = guild.get_channel(1056738639813546034)  # type: ignore
        dev_role: discord.Role = guild.get_role(1058049513111167016)  # type: ignore
        game_role: discord.Role = guild.get_role(1058052420627857558)  # type: ignore
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

            Após isso você poderá escolher uma das linguagens abaixo.
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
        embed_intro.set_thumbnail(url=bot_icon_url)
        embed_intro.set_footer(
            text="Um abraço da FrontlessTeam. ❤️.", icon_url=bot_icon_url
        )

        options: list[discord.SelectOption] = []
        await self.bot.db_connected.wait()
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM programming_languages_roles")
            roles: list[tuple[str, str, str]] = await cursor.fetchall()

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
                embed=embed_intro,
            )
        else:
            await ctx.respond(
                view=PersistentView(max_val=mx_len, options=options),
                embed=embed_intro,
            )

    # ██╗    ██╗ █████╗ ██████╗ ███╗   ██╗    ██╗   ██╗███████╗███████╗██████╗
    # ██║    ██║██╔══██╗██╔══██╗████╗  ██║    ██║   ██║██╔════╝██╔════╝██╔══██╗
    # ██║ █╗ ██║███████║██████╔╝██╔██╗ ██║    ██║   ██║███████╗█████╗  ██████╔╝
    # ██║███╗██║██╔══██║██╔══██╗██║╚██╗██║    ██║   ██║╚════██║██╔══╝  ██╔══██╗
    # ╚███╔███╔╝██║  ██║██║  ██║██║ ╚████║    ╚██████╔╝███████║███████╗██║  ██║
    #  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝     ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝

    @commands.slash_command(
        name="warn_user", description="Warns the user [just one time]"
    )
    @commands.has_role(1056755317419028560)
    async def warn_user(
        self,
        ctx: discord.ApplicationContext,
        user: discord.User,
        reason: str,
    ) -> None:
        """."""
        user_id: int = user.id

        if user_id == ctx.guild.owner_id:  # type: ignore
            await ctx.respond("Dono do servidor detectado, ação cancelada.")
            return

        if user_id == self.bot.user.id:
            await ctx.respond("FrontlessBot detectado, ação cancelada.")
            return

        await self.bot.db_connected.wait()
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM active_warns WHERE user_id=?", (user_id,)
            )
            user_warn: typing.Any = await cursor.fetchall()
        if not user_warn:
            print("user not found in warn table")
            warn_type: str = "moderation"
            await self.bot.db_connected.wait()
            async with self.bot.db.cursor() as cursor:
                exec_cmd: str = "INSERT OR IGNORE INTO active_warns(user_name, user_discriminator, user_id, reason, type, unix_date) VALUES(?,?,?,?,?,?)"
                exec_cmd2: str = "INSERT OR IGNORE INTO warns_history(user_name, user_discriminator, user_id, reason, type, unix_date) VALUES(?,?,?,?,?,?)"
                await cursor.execute(
                    exec_cmd,
                    (
                        user.name,
                        user.discriminator,
                        user_id,
                        reason,
                        warn_type,
                        int(time()),
                    ),
                )
                await cursor.execute(
                    exec_cmd2,
                    (
                        user.name,
                        user.discriminator,
                        user_id,
                        reason,
                        warn_type,
                        int(time()),
                    ),
                )
            await self.bot.db.commit()
            mod_log_chan: discord.TextChannel = ctx.guild.get_channel(mod_logs_chan_id)
            timeout_embed: discord.Embed = discord.Embed(
                title="Aviso da moderação",
                description=f"{user.mention}, este é um aviso da moderação, a proxima sinalização será provida de um timeout.",
                colour=discord.Colour.yellow(),
                timestamp=datetime.now(),
            )
            timeout_embed.set_thumbnail(url=user.avatar.url)

            await mod_log_chan.send(embed=timeout_embed)
        else:
            await ctx.respond(
                f"usuário {user.mention} já previamente avisado, aplicar timeout?",
                view=TimeOutPromptView(
                    user=user,
                    delete_func=ctx.delete,
                    reason=reason,
                    database=self.bot.db,
                    bot_event_wait_func=self.bot.db_connected.wait,
                ),
            )

    # ██████╗ ███████╗██╗   ██╗ ██████╗ ██╗  ██╗███████╗    ██╗    ██╗ █████╗ ██████╗ ███╗   ██╗
    # ██╔══██╗██╔════╝██║   ██║██╔═══██╗██║ ██╔╝██╔════╝    ██║    ██║██╔══██╗██╔══██╗████╗  ██║
    # ██████╔╝█████╗  ██║   ██║██║   ██║█████╔╝ █████╗      ██║ █╗ ██║███████║██████╔╝██╔██╗ ██║
    # ██╔══██╗██╔══╝  ╚██╗ ██╔╝██║   ██║██╔═██╗ ██╔══╝      ██║███╗██║██╔══██║██╔══██╗██║╚██╗██║
    # ██║  ██║███████╗ ╚████╔╝ ╚██████╔╝██║  ██╗███████╗    ╚███╔███╔╝██║  ██║██║  ██║██║ ╚████║
    # ╚═╝  ╚═╝╚══════╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝╚══════╝     ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝

    @commands.slash_command(name="remove_warn", description="Revokes the warning")
    @commands.has_role(1056755317419028560)
    async def remove_warn(
        self, ctx: discord.ApplicationContext, user: discord.User
    ) -> None:
        """."""
        user_id: int = user.id

        if user_id == ctx.guild.owner_id:  # type: ignore
            await ctx.respond("Dono do servidor detectado, ação cancelada.")
            return

        if user_id == self.bot.user.id:
            await ctx.respond("FrontlessBot detectado, ação cancelada.")
            return

        await self.bot.db_connected.wait()
        async with self.bot.db.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM active_warns WHERE user_id=?", (user_id,)
            )
            user_warn: typing.Any = await cursor.fetchall()

        if not user_warn:
            print("user not found in warn table")
            await ctx.respond(
                f"O usuário {user.mention} não tem nenhum aviso no banco de dados."
            )
        else:
            await self.bot.db_connected.wait()
            async with self.bot.db.cursor() as cursor:
                del_cmd: str = "DELETE FROM active_warns WHERE user_id=?"
                await cursor.execute(del_cmd, (user_id,))
            await self.bot.db.commit()
            mod_log_chan: discord.TextChannel = ctx.guild.get_channel(mod_logs_chan_id)
            timeout_embed: discord.Embed = discord.Embed(
                title="Aviso da moderação",
                description=f"aviso do {user.mention} revogado pelo moderador {ctx.user.mention}.",
                colour=discord.Colour.darker_grey(),
                timestamp=datetime.now(),
            )
            timeout_embed.set_thumbnail(url=user.avatar.url)

            await mod_log_chan.send(embed=timeout_embed)
            await ctx.respond(f"Removendo aviso do usuário {user.mention}.")

    # ██╗    ██╗ █████╗ ██████╗ ███╗   ██╗    ██████╗ ███████╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗
    # ██║    ██║██╔══██╗██╔══██╗████╗  ██║    ██╔══██╗██╔════╝██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝
    # ██║ █╗ ██║███████║██████╔╝██╔██╗ ██║    ██████╔╝█████╗  ██║   ██║██║   ██║█████╗  ███████╗   ██║
    # ██║███╗██║██╔══██║██╔══██╗██║╚██╗██║    ██╔══██╗██╔══╝  ██║▄▄ ██║██║   ██║██╔══╝  ╚════██║   ██║
    # ╚███╔███╔╝██║  ██║██║  ██║██║ ╚████║    ██║  ██║███████╗╚██████╔╝╚██████╔╝███████╗███████║   ██║
    #  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝

    @commands.slash_command(name="warn_request", description="Requests a user warning")
    async def warn_request(
        self, ctx: discord.ApplicationContext, user: discord.User, reason: str
    ) -> None:
        """."""
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
                guild=ctx.guild,
                wait_database_function=self.bot.db_connected.wait,
                bot=self.bot,
                timeout=1800,
            ),  # 1800
        )

    # ████████╗██╗███╗   ███╗███████╗ ██████╗ ██╗   ██╗████████╗    ██╗   ██╗███████╗███████╗██████╗
    # ╚══██╔══╝██║████╗ ████║██╔════╝██╔═══██╗██║   ██║╚══██╔══╝    ██║   ██║██╔════╝██╔════╝██╔══██╗
    #    ██║   ██║██╔████╔██║█████╗  ██║   ██║██║   ██║   ██║       ██║   ██║███████╗█████╗  ██████╔╝
    #    ██║   ██║██║╚██╔╝██║██╔══╝  ██║   ██║██║   ██║   ██║       ██║   ██║╚════██║██╔══╝  ██╔══██╗
    #    ██║   ██║██║ ╚═╝ ██║███████╗╚██████╔╝╚██████╔╝   ██║       ╚██████╔╝███████║███████╗██║  ██║
    #    ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚═════╝    ╚═╝        ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝

    @commands.slash_command(name="timeout_user", description="Timeouts the user")
    @commands.has_role(1056755317419028560)
    async def timeout_user(
        self,
        ctx: discord.ApplicationContext,
        user: discord.User,
        reason: str,
    ) -> None:
        """."""
        user_id: int = user.id
        if user_id == ctx.guild.owner_id:  # type: ignore
            await ctx.respond("Dono do servidor detectado, ação cancelada.")
            return

        if user_id == self.bot.user.id:
            await ctx.respond("FrontlessBot detectado, ação cancelada.")
            return

        await ctx.response.send_message(
            content="Selecione o timeout a ser aplicado.",
            view=TimeOutDropdownMenuView(
                delete_func=ctx.delete,
                user=user,
                delete_parent_msg_func=None,
                reason=reason,
                database=self.bot.db,
                bot_event_wait_func=self.bot.db_connected.wait,
            ),
        )

    # ██████╗ ███████╗██╗   ██╗ ██████╗ ██╗  ██╗███████╗    ████████╗██╗███╗   ███╗███████╗ ██████╗ ██╗   ██╗████████╗
    # ██╔══██╗██╔════╝██║   ██║██╔═══██╗██║ ██╔╝██╔════╝    ╚══██╔══╝██║████╗ ████║██╔════╝██╔═══██╗██║   ██║╚══██╔══╝
    # ██████╔╝█████╗  ██║   ██║██║   ██║█████╔╝ █████╗         ██║   ██║██╔████╔██║█████╗  ██║   ██║██║   ██║   ██║
    # ██╔══██╗██╔══╝  ╚██╗ ██╔╝██║   ██║██╔═██╗ ██╔══╝         ██║   ██║██║╚██╔╝██║██╔══╝  ██║   ██║██║   ██║   ██║
    # ██║  ██║███████╗ ╚████╔╝ ╚██████╔╝██║  ██╗███████╗       ██║   ██║██║ ╚═╝ ██║███████╗╚██████╔╝╚██████╔╝   ██║
    # ╚═╝  ╚═╝╚══════╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝╚══════╝       ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚═════╝    ╚═╝

    @commands.slash_command(name="revoke_timeout", description="Timeouts the user")
    @commands.has_role(1056755317419028560)
    async def revoke_timeout(
        self,
        ctx: discord.ApplicationContext,
        user: discord.User,
    ) -> None:
        """."""
        await user.remove_timeout()
        await self.bot.db_connected.wait()
        async with self.bot.db.cursor() as cursor:
            del_cmd: str = "DELETE FROM active_timeouts WHERE user_id=?"
            await cursor.execute(del_cmd, (int(user.id),))
        await self.bot.db.commit()
        mod_log_chan: discord.TextChannel = ctx.guild.get_channel(mod_logs_chan_id)
        timeout_embed: discord.Embed = discord.Embed(
            title="Aviso da moderação",
            description=f"Timeout do {user.mention} revogado pelo moderador {ctx.user.mention}.",
            colour=discord.Colour.darker_grey(),
            timestamp=datetime.now(),
        )
        timeout_embed.set_thumbnail(url=user.avatar.url)

        await mod_log_chan.send(embed=timeout_embed)
        await ctx.respond(f"Removido timeout do {user.mention}")

    # ████████╗██╗███╗   ███╗ ██████╗ ██╗   ██╗████████╗    ██████╗ ███████╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗
    # ╚══██╔══╝██║████╗ ████║██╔═══██╗██║   ██║╚══██╔══╝    ██╔══██╗██╔════╝██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝
    #    ██║   ██║██╔████╔██║██║   ██║██║   ██║   ██║       ██████╔╝█████╗  ██║   ██║██║   ██║█████╗  ███████╗   ██║
    #    ██║   ██║██║╚██╔╝██║██║   ██║██║   ██║   ██║       ██╔══██╗██╔══╝  ██║▄▄ ██║██║   ██║██╔══╝  ╚════██║   ██║
    #    ██║   ██║██║ ╚═╝ ██║╚██████╔╝╚██████╔╝   ██║       ██║  ██║███████╗╚██████╔╝╚██████╔╝███████╗███████║   ██║
    #    ╚═╝   ╚═╝╚═╝     ╚═╝ ╚═════╝  ╚═════╝    ╚═╝       ╚═╝  ╚═╝╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝

    @commands.slash_command(name="timeout_request", description="Timeouts the user")
    async def timeout_request(
        self,
        ctx: discord.ApplicationContext,
        user: discord.User,
        reason: str,
        nivel: int,
    ) -> None:
        """."""
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
                    user=user,
                    reason=reason,
                    database=self.bot.db,
                    guild=ctx.guild,
                    wait_database_function=self.bot.db_connected.wait,
                    bot=self.bot,
                    timeout=1800,
                    nivel=nivel,
                ),  # 1800
            )
        else:
            await ctx.respond("`Nivel` precisa ser menor que 4")

    # ██████╗  █████╗ ███╗   ██╗    ██╗   ██╗███████╗███████╗██████╗
    # ██╔══██╗██╔══██╗████╗  ██║    ██║   ██║██╔════╝██╔════╝██╔══██╗
    # ██████╔╝███████║██╔██╗ ██║    ██║   ██║███████╗█████╗  ██████╔╝
    # ██╔══██╗██╔══██║██║╚██╗██║    ██║   ██║╚════██║██╔══╝  ██╔══██╗
    # ██████╔╝██║  ██║██║ ╚████║    ╚██████╔╝███████║███████╗██║  ██║
    # ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝     ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝

    @commands.slash_command(name="ban_user", description="bans a user")
    @commands.has_role(1056755317419028560)
    async def ban_user(
        self,
        ctx: discord.ApplicationContext,
        user: discord.User,
        reason: str,
    ) -> None:
        """."""
        user_id: int = user.id
        if user_id == ctx.guild.owner_id:  # type: ignore
            await ctx.respond("Dono do servidor detectado, ação cancelada.")
            return

        if user_id == self.bot.user.id:
            await ctx.respond("FrontlessBot detectado, ação cancelada.")
            return

        await ctx.response.send_message(
            content="Confirmar banimento de usuário.",
            view=BanConfirmationView(
                delete_func=ctx.delete,
                user=user,
                reason=reason,
                database=self.bot.db,
                bot_event_wait_func=self.bot.db_connected.wait,
            ),
        )

    # ██╗   ██╗███╗   ██╗██████╗  █████╗ ███╗   ██╗    ██╗   ██╗███████╗███████╗██████╗
    # ██║   ██║████╗  ██║██╔══██╗██╔══██╗████╗  ██║    ██║   ██║██╔════╝██╔════╝██╔══██╗
    # ██║   ██║██╔██╗ ██║██████╔╝███████║██╔██╗ ██║    ██║   ██║███████╗█████╗  ██████╔╝
    # ██║   ██║██║╚██╗██║██╔══██╗██╔══██║██║╚██╗██║    ██║   ██║╚════██║██╔══╝  ██╔══██╗
    # ╚██████╔╝██║ ╚████║██████╔╝██║  ██║██║ ╚████║    ╚██████╔╝███████║███████╗██║  ██║
    #  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝     ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝

    @commands.slash_command(name="unban_user", description="unbans a user")
    @commands.has_role(1056755317419028560)
    async def unban_user(
        self,
        ctx: discord.ApplicationContext,
        reason: str,
    ) -> None:
        """."""
        guild: discord.Guild = ctx.guild

        bans: list = await guild.bans().flatten()

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

        if bans == []:
            await ctx.response.send_message(content="Não existem usuários banidos.")
        else:
            await ctx.response.send_message(
                content="Selecione o usuário para desbanir",
                view=UserUnbanView(
                    delete_func=ctx.delete,
                    reason=reason,
                    database=self.bot.db,
                    bot_event_wait_func=self.bot.db_connected.wait,
                    options=options,
                    max_val=mx_val,
                    bans=banned_users,
                ),
            )

    # ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗     ██╗      ██████╗  ██████╗██╗  ██╗
    # ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗    ██║     ██╔═══██╗██╔════╝██║ ██╔╝
    # ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝    ██║     ██║   ██║██║     █████╔╝
    # ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗    ██║     ██║   ██║██║     ██╔═██╗
    # ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║    ███████╗╚██████╔╝╚██████╗██║  ██╗
    # ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝    ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝

    @commands.slash_command(name="lock", description="locks the server in case of raid")
    @commands.has_role(1056755317419028560)
    async def lock(self, ctx: discord.ApplicationContext) -> None:
        """."""
        guild: discord.Guild = ctx.guild
        user: discord.User = ctx.user
        for category in guild.categories:
            if category.name.lower() == "server_lock":
                is_server_lock: bool = False
                lock_category: discord.CategoryChannel = category
                break
        else:
            is_server_lock: bool = True

        if is_server_lock:
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
            embed.set_author(name="Frontless Programming", icon_url=bot_icon_url)
            embed.set_footer(
                text="Atenciosamente, FrontlessTeam.", icon_url=bot_icon_url
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

            ins_cmd: str = "INSERT OR IGNORE INTO lock_state(role_id, channel_id, permissions_bin, unix_date) VALUES(?,?,?,?)"
            await self.bot.db_connected.wait()
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM lock_state")
                for role in guild.roles:
                    for chan in guild.channels:
                        perms: discord.Permissions = chan.permissions_for(role)
                        await cursor.execute(
                            ins_cmd,
                            (
                                int(role.id),
                                int(chan.id),
                                int(perms.value),
                                curr_unix_time,
                            ),
                        )
            await self.bot.db.commit()

            for role in roles_list:
                for chan in chan_list:
                    print(role, chan)
                    await chan.set_permissions(target=role, overwrite=ever_perms)

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

    # ██████╗ ███████╗███████╗████████╗ ██████╗ ██████╗ ███████╗
    # ██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝
    # ██████╔╝█████╗  ███████╗   ██║   ██║   ██║██████╔╝█████╗
    # ██╔══██╗██╔══╝  ╚════██║   ██║   ██║   ██║██╔══██╗██╔══╝
    # ██║  ██║███████╗███████║   ██║   ╚██████╔╝██║  ██║███████╗
    # ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝

    @commands.slash_command(name="restore", description="restore the server lock")
    @commands.is_owner()
    async def restore(self, ctx: discord.ApplicationContext) -> None:
        """."""
        guild: discord.Guild = ctx.guild
        for category in guild.categories:
            if category.name.lower() == "server_lock":
                is_server_lock: bool = True
                lock_category: discord.CategoryChannel = category
                break
        else:
            is_server_lock: bool = False

        if is_server_lock:
            await ctx.response.send_message(content="Restaurando servidor.")
            perms_dict: dict[str, int] = discord.Permissions.VALID_FLAGS

            print(lock_category)
            print(perms_dict)
            await self.bot.db_connected.wait()
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("SELECT * FROM lock_state")
                state = await cursor.fetchall()

            for i in state:
                chan: discord.TextChannel = guild.get_channel(int(i[1]))
                role: discord.Role = guild.get_role(int(i[0]))
                perms_int: discord.Permissions = discord.Permissions(int(i[2]))
                perms: discord.PermissionOverwrite = discord.PermissionOverwrite(
                    add_reactions=bool(
                        (int(perms_int.value) & int(perms_dict["add_reactions"]))
                        == int(perms_dict["add_reactions"])
                    ),
                    administrator=bool(
                        (int(perms_int.value) & int(perms_dict["administrator"]))
                        == int(perms_dict["administrator"])
                    ),
                    attach_files=bool(
                        (int(perms_int.value) & int(perms_dict["attach_files"]))
                        == int(perms_dict["attach_files"])
                    ),
                    ban_members=bool(
                        (int(perms_int.value) & int(perms_dict["ban_members"]))
                        == int(perms_dict["ban_members"])
                    ),
                    change_nickname=bool(
                        (int(perms_int.value) & int(perms_dict["change_nickname"]))
                        == int(perms_dict["change_nickname"])
                    ),
                    connect=bool(
                        (int(perms_int.value) & int(perms_dict["connect"]))
                        == int(perms_dict["connect"])
                    ),
                    create_instant_invite=bool(
                        (
                            int(perms_int.value)
                            & int(perms_dict["create_instant_invite"])
                        )
                        == int(perms_dict["create_instant_invite"])
                    ),
                    create_private_threads=bool(
                        (
                            int(perms_int.value)
                            & int(perms_dict["create_private_threads"])
                        )
                        == int(perms_dict["create_private_threads"])
                    ),
                    create_public_threads=bool(
                        (
                            int(perms_int.value)
                            & int(perms_dict["create_public_threads"])
                        )
                        == int(perms_dict["create_public_threads"])
                    ),
                    deafen_members=bool(
                        (int(perms_int.value) & int(perms_dict["deafen_members"]))
                        == int(perms_dict["deafen_members"])
                    ),
                    embed_links=bool(
                        (int(perms_int.value) & int(perms_dict["embed_links"]))
                        == int(perms_dict["embed_links"])
                    ),
                    external_emojis=bool(
                        (int(perms_int.value) & int(perms_dict["external_emojis"]))
                        == int(perms_dict["external_emojis"])
                    ),
                    external_stickers=bool(
                        (int(perms_int.value) & int(perms_dict["external_stickers"]))
                        == int(perms_dict["external_stickers"])
                    ),
                    kick_members=bool(
                        (int(perms_int.value) & int(perms_dict["kick_members"]))
                        == int(perms_dict["kick_members"])
                    ),
                    manage_channels=bool(
                        (int(perms_int.value) & int(perms_dict["manage_channels"]))
                        == int(perms_dict["manage_channels"])
                    ),
                    manage_emojis=bool(
                        (int(perms_int.value) & int(perms_dict["manage_emojis"]))
                        == int(perms_dict["manage_emojis"])
                    ),
                    manage_emojis_and_stickers=bool(
                        (
                            int(perms_int.value)
                            & int(perms_dict["manage_emojis_and_stickers"])
                        )
                        == int(perms_dict["manage_emojis_and_stickers"])
                    ),
                    manage_events=bool(
                        (int(perms_int.value) & int(perms_dict["manage_events"]))
                        == int(perms_dict["manage_events"])
                    ),
                    manage_guild=bool(
                        (int(perms_int.value) & int(perms_dict["manage_guild"]))
                        == int(perms_dict["manage_guild"])
                    ),
                    manage_messages=bool(
                        (int(perms_int.value) & int(perms_dict["manage_messages"]))
                        == int(perms_dict["manage_messages"])
                    ),
                    manage_nicknames=bool(
                        (int(perms_int.value) & int(perms_dict["manage_nicknames"]))
                        == int(perms_dict["manage_nicknames"])
                    ),
                    manage_permissions=bool(
                        (int(perms_int.value) & int(perms_dict["manage_permissions"]))
                        == int(perms_dict["manage_permissions"])
                    ),
                    manage_roles=bool(
                        (int(perms_int.value) & int(perms_dict["manage_roles"]))
                        == int(perms_dict["manage_roles"])
                    ),
                    manage_threads=bool(
                        (int(perms_int.value) & int(perms_dict["manage_threads"]))
                        == int(perms_dict["manage_threads"])
                    ),
                    manage_webhooks=bool(
                        (int(perms_int.value) & int(perms_dict["manage_webhooks"]))
                        == int(perms_dict["manage_webhooks"])
                    ),
                    mention_everyone=bool(
                        (int(perms_int.value) & int(perms_dict["mention_everyone"]))
                        == int(perms_dict["mention_everyone"])
                    ),
                    moderate_members=bool(
                        (int(perms_int.value) & int(perms_dict["moderate_members"]))
                        == int(perms_dict["moderate_members"])
                    ),
                    move_members=bool(
                        (int(perms_int.value) & int(perms_dict["move_members"]))
                        == int(perms_dict["move_members"])
                    ),
                    mute_members=bool(
                        (int(perms_int.value) & int(perms_dict["mute_members"]))
                        == int(perms_dict["mute_members"])
                    ),
                    priority_speaker=bool(
                        (int(perms_int.value) & int(perms_dict["priority_speaker"]))
                        == int(perms_dict["priority_speaker"])
                    ),
                    read_message_history=bool(
                        (int(perms_int.value) & int(perms_dict["read_message_history"]))
                        == int(perms_dict["read_message_history"])
                    ),
                    read_messages=bool(
                        (int(perms_int.value) & int(perms_dict["read_messages"]))
                        == int(perms_dict["read_messages"])
                    ),
                    request_to_speak=bool(
                        (int(perms_int.value) & int(perms_dict["request_to_speak"]))
                        == int(perms_dict["request_to_speak"])
                    ),
                    send_messages=bool(
                        (int(perms_int.value) & int(perms_dict["send_messages"]))
                        == int(perms_dict["send_messages"])
                    ),
                    send_messages_in_threads=bool(
                        (
                            int(perms_int.value)
                            & int(perms_dict["send_messages_in_threads"])
                        )
                        == int(perms_dict["send_messages_in_threads"])
                    ),
                    send_tts_messages=bool(
                        (int(perms_int.value) & int(perms_dict["send_tts_messages"]))
                        == int(perms_dict["send_tts_messages"])
                    ),
                    speak=bool(
                        (int(perms_int.value) & int(perms_dict["speak"]))
                        == int(perms_dict["speak"])
                    ),
                    start_embedded_activities=bool(
                        (
                            int(perms_int.value)
                            & int(perms_dict["start_embedded_activities"])
                        )
                        == int(perms_dict["start_embedded_activities"])
                    ),
                    stream=bool(
                        (int(perms_int.value) & int(perms_dict["stream"]))
                        == int(perms_dict["stream"])
                    ),
                    use_application_commands=bool(
                        (
                            int(perms_int.value)
                            & int(perms_dict["use_application_commands"])
                        )
                        == int(perms_dict["use_application_commands"])
                    ),
                    use_external_emojis=bool(
                        (int(perms_int.value) & int(perms_dict["use_external_emojis"]))
                        == int(perms_dict["use_external_emojis"])
                    ),
                    use_external_stickers=bool(
                        (
                            int(perms_int.value)
                            & int(perms_dict["use_external_stickers"])
                        )
                        == int(perms_dict["use_external_stickers"])
                    ),
                    use_slash_commands=bool(
                        (int(perms_int.value) & int(perms_dict["use_slash_commands"]))
                        == int(perms_dict["use_slash_commands"])
                    ),
                    use_voice_activation=bool(
                        (int(perms_int.value) & int(perms_dict["use_voice_activation"]))
                        == int(perms_dict["use_voice_activation"])
                    ),
                    view_audit_log=bool(
                        (int(perms_int.value) & int(perms_dict["view_audit_log"]))
                        == int(perms_dict["view_audit_log"])
                    ),
                    view_channel=bool(
                        (int(perms_int.value) & int(perms_dict["view_channel"]))
                        == int(perms_dict["view_channel"])
                    ),
                    view_guild_insights=bool(
                        (int(perms_int.value) & int(perms_dict["view_guild_insights"]))
                        == int(perms_dict["view_guild_insights"])
                    ),
                )
                print(f"{chan.name =}\t{role.name =}")
                await chan.set_permissions(target=role, overwrite=perms)
                if not chan.permissions_synced:
                    await chan.edit(sync_permissions=True)
                    await chan.edit(slowmode_delay=5)

            for chan_ in lock_category.channels:
                await chan_.delete()
            await lock_category.delete()

            await self.bot.db_connected.wait()
            async with self.bot.db.cursor() as cursor:
                await cursor.execute("DELETE FROM lock_state")
            await self.bot.db.commit()
        else:
            await ctx.response.send_message(content="Servidor não trancado.")

    #  ██████╗  ███╗   ██╗          ██████╗  ███████╗  █████╗  ██████╗  ██╗   ██╗
    # ██╔═══██╗ ████╗  ██║          ██╔══██╗ ██╔════╝ ██╔══██╗ ██╔══██╗ ╚██╗ ██╔╝
    # ██║   ██║ ██╔██╗ ██║          ██████╔╝ █████╗   ███████║ ██║  ██║  ╚████╔╝
    # ██║   ██║ ██║╚██╗██║          ██╔══██╗ ██╔══╝   ██╔══██║ ██║  ██║   ╚██╔╝
    # ╚██████╔╝ ██║ ╚████║ ███████╗ ██║  ██║ ███████╗ ██║  ██║ ██████╔╝    ██║
    #  ╚═════╝  ╚═╝  ╚═══╝ ╚══════╝ ╚═╝  ╚═╝ ╚══════╝ ╚═╝  ╚═╝ ╚═════╝     ╚═╝

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Listener para reativar os botões ao iniciar do bot"""
        options: list[discord.SelectOption] = []
        await self.bot.db_connected.wait()
        async with self.bot.db.cursor() as cursor:
            await cursor.execute("SELECT * FROM programming_languages_roles")
            roles: list[tuple[str, str, str]] = await cursor.fetchall()

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
        if not self.bot.persistent_views_added:
            self.bot.add_view(PersistentView(max_val=mx_len, options=options))
            self.bot.persistent_views_added = True

    # ███████╗██████╗ ██████╗  ██████╗ ██████╗     ██╗  ██╗ █████╗ ███╗   ██╗██████╗ ██╗     ███████╗██████╗
    # ██╔════╝██╔══██╗██╔══██╗██╔═══██╗██╔══██╗    ██║  ██║██╔══██╗████╗  ██║██╔══██╗██║     ██╔════╝██╔══██╗
    # █████╗  ██████╔╝██████╔╝██║   ██║██████╔╝    ███████║███████║██╔██╗ ██║██║  ██║██║     █████╗  ██████╔╝
    # ██╔══╝  ██╔══██╗██╔══██╗██║   ██║██╔══██╗    ██╔══██║██╔══██║██║╚██╗██║██║  ██║██║     ██╔══╝  ██╔══██╗
    # ███████╗██║  ██║██║  ██║╚██████╔╝██║  ██║    ██║  ██║██║  ██║██║ ╚████║██████╔╝███████╗███████╗██║  ██║
    # ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingRole):
            await ctx.send(
                f"Permissão negada {ctx.author.name} esse comando só pode ser usado por um administrador.",  # pylint: disable=line-too-long
                reference=ctx.message,
                delete_after=4,
            )
        elif isinstance(error, commands.NotOwner):
            await ctx.send(
                f"Permissão negada {ctx.author.name} esse comando só pode ser usado pelo dono do servidor.",  # pylint: disable=line-too-long
                reference=ctx.message,
                delete_after=4,
            )
        else:
            await ctx.send(
                "Um erro inesperado ocorreu.",  # pylint: disable=line-too-long
                reference=ctx.message,
                delete_after=4,
            )
            raise error  # Here we raise other errors to ensure they aren't ignored


# ███████╗███████╗████████╗██╗   ██╗██████╗
# ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗
# ███████╗█████╗     ██║   ██║   ██║██████╔╝
# ╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝
# ███████║███████╗   ██║   ╚██████╔╝██║
# ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝


def setup(bot) -> None:
    """Function that sets up the cog for the bot"""
    bot.add_cog(Adminstrative(bot))
