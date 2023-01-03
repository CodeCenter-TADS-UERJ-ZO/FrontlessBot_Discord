"""Generic Stuff"""
import discord
from discord.ext import commands, pages

# pylint: disable=line-too-long too-many-locals

bot_icon_url: str = "https://cdn.discordapp.com/app-icons/1056943227183321118/08902aef3ee87acc3e69081c0a012b71.png?size=2048"


commands_desc: dict[str, dict[str, str]] = {
    "Generic": {
        "`/help`    `APENAS ADMINISTRADORES`": """
        Exibe as regras
        Uso:
                `/help`"""
    },
    "Administrative": {
        "`/warn_request`": """Levanta uma votação para pedir um aviso a um usuário.
        Uso:
                `/warn_request` `usuário` `motivo`
        Argumentos:
                `usuário`: O usuário no qual você deseja que um aviso seja aplicado.
                `motivo`: O motivo por trás do aviso.
        Observações:
                A votação ficará disponível por 30 minutos antes de ser fechada, caso o resultado seja positivo um pedido será enviado aos moderadores e os mesmos terão 48 horas para acatar a solicitação, caso contrário, ela será descartada.""",  # pylint: disable=line-too-long
        "`/timeout_request`": """Levanta uma votação para pedir um timeout a um usuário.
        Uso:
                `/timeout_request` `usuário` `motivo` `nivel`
        Argumentos:
                `usuário`: O usuário no qual você deseja que o timeout seja aplicado.
                `motivo`: O motivo por trás do timeout.
                `nivel`: O nivel do timeout, estão disponíveis três níveis:
                        • `1`: Timeout de 1 minuto.
                        • `2`: Timeout de 5 minutos.
                        • `3`: Timeout de 10 minutos.
        Exemplo:
                `/timeout_request` `@iariM` `exemplo` `2`
        *Aplica um timeout de 5 minutos no usuário @iariM pelo motivo "Exemplo"*
        Observações:
                A votação ficará disponível por 30 minutos antes de ser fechada, caso o resultado seja positivo um pedido será enviado aos moderadores e os mesmos terão 48 horas para acatar a solicitação, caso contrário, ela será descartada.""",  # pylint: disable=line-too-long
        "`/regras`    `APENAS ADMINISTRADORES`": """
        Exibe as regras
        Uso:
                `/regras`""",
        "`/language_selection`    `APENAS ADMINISTRADORES`": """
        Exibe o menu de seleção de cargos de programação
        Uso:
                `/language_selection`""",
        "`/create_category`    `APENAS ADMINISTRADORES`": """
        Cria uma categoria e configura todos os canais e cargos
        Uso:
                `/create_category` `nome` `tipo`
        Argumentos:
                `nome`: O nome da categoria a ser criada.
                `tipo`: O tipo da categoria, deve ser um desses dois:
                        • `code`
                        • `game`""",
        "`/welcome`    `APENAS ADMINISTRADORES`": """
        Exibe a tela de boas-vindas
        Uso:
                `/welcome`""",
        "`/warn_user`    `APENAS ADMINISTRADORES`": """
        Aplica um aviso ao usuário, apenas uma unica vez
        Uso:
                `/warn_user` `usuário` `motivo`
        Argumentos:
                `usuário`: O usuário no qual você deseja aplicar o aviso.
                `motivo`: O motivo por trás do aviso.""",
        "`/remove_warn`    `APENAS ADMINISTRADORES`": """
        Revoga um aviso aplicado a um usuário.
        Uso:
                `/remove_warn` `usuário`
        Argumentos:
                `usuário`: O usuário no qual você deseja revogar o aviso.""",
        "`/timeout_user`    `APENAS ADMINISTRADORES`": """
        Aplica um timeout a um usuário
        Uso:
                `/timeout_user` `usuário` `motivo`
        Argumentos:
                `usuário`: O usuário no qual você aplicar o timeout.
                `motivo`: O motivo por trás do timeout.""",
        "`/revoke_timeout`    `APENAS ADMINISTRADORES`": """
        Revoga o timeout um usuário
        Uso:
                `/revoke_timeout` `usuário`
        Argumentos:
                `usuário`: O usuário no qual você deseja revogar o timeout.""",
        "`/ban_user`    `APENAS ADMINISTRADORES`": """
        Bane um usuário.
        Uso:
                `/ban_user` `usuário` `motivo`
        Argumentos:
                `usuário`: O usuário no qual você deseja que um ban seja aplicado.
                `motivo`: O motivo por trás do banimento.""",
        "`/unban_user`    `APENAS ADMINISTRADORES`": """
        Revoga o banimento de um usuário.
        Uso:
                `/unban_user` `usuário` `motivo`
        Argumentos:
                `usuário`: O usuário no qual você deseja revogar o banimento.
                `motivo`: O motivo por trás da remoção.""",
        "`/lock`    `APENAS ADMINISTRADORES`": """
        Tranca o servidor em caso de raids.
        Uso:
                `/lock`""",
        "`/restore`    `APENAS DONO(A) DO SERVIDOR`": """
        Caso o servidor esteja trancado por conta de raids, este comando deverá ser usado pelo dono do servidor para restaurar o estado.
        Uso:
                `/restore`""",
    },
}


class PersistentView(discord.ui.View):
    """."""

    def __init__(self) -> None:
        super().__init__(timeout=None)


class Generic(commands.Cog):
    """Cog used to manage all Administrative commands"""

    # pylint: disable=line-too-long

    def __init__(self, bot: discord.Bot) -> None:
        self.bot: discord.Bot = bot
        self.bot.persistent_views_added = False

    @commands.slash_command(
        name="help",
        description="\nExibe as regras\nUso:\n\t/help",
    )
    @commands.has_role(1056755317419028560)
    async def help_command(self, ctx: discord.ApplicationContext) -> None:
        """."""
        _pages: list[pages.Page] = []

        buttons: list[pages.PaginatorButton] = [
            pages.PaginatorButton(
                "first", label="<<-", style=discord.ButtonStyle.green
            ),
            pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
            pages.PaginatorButton(
                "page_indicator", style=discord.ButtonStyle.gray, disabled=True
            ),
            pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
            pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
        ]

        if commands_desc:
            for _k, _v in commands_desc.items():
                ebd: discord.Embed = discord.Embed(
                    title=_k,
                    description=f"Comandos da cog {_k}",
                )
                for _v_k, _v_v in _v.items():
                    ebd.add_field(
                        name=_v_k,
                        value=_v_v,
                        inline=False,
                    )

                curr_page: pages.Page = pages.Page(embeds=[ebd])

                _pages.append(curr_page)
        else:
            cogs_list: list[discord.Cog] = []

            for cog_n in self.bot.cogs:
                cog: discord.Cog = self.bot.get_cog(cog_n)
                cogs_list.append(cog)

            for _cog in cogs_list:

                ebd: discord.Embed = discord.Embed(
                    title=_cog.qualified_name,
                    description=f"Comandos da cog {_cog.qualified_name}",
                )

                for cmd in _cog.walk_commands():
                    if not cmd.options:
                        opts_str: str = ""
                    else:
                        opts_names: list[str] = []
                        for i in cmd.options:
                            opts_names.append(str(i.name))
                        base_str: str = ", ".join(opts_names)
                        opts_str: str = f": {base_str}"

                    ebd.add_field(
                        name=f"{cmd.name}{opts_str}",
                        value=cmd.description,
                        inline=False,
                    )

                curr_page: pages.Page = pages.Page(embeds=[ebd])

                _pages.append(curr_page)

        paginator: pages.Paginator = pages.Paginator(
            pages=_pages,
            show_indicator=True,
            use_default_buttons=False,
            custom_buttons=buttons,
            loop_pages=True,
            timeout=None,
            custom_view=PersistentView(),
        )

        await paginator.respond(ctx.interaction)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Listener para reativar os botões ao iniciar do bot"""
        _pages: list[pages.Page] = []

        buttons: list[pages.PaginatorButton] = [
            pages.PaginatorButton(
                "first", label="<<-", style=discord.ButtonStyle.green
            ),
            pages.PaginatorButton("prev", label="<-", style=discord.ButtonStyle.green),
            pages.PaginatorButton(
                "page_indicator", style=discord.ButtonStyle.gray, disabled=True
            ),
            pages.PaginatorButton("next", label="->", style=discord.ButtonStyle.green),
            pages.PaginatorButton("last", label="->>", style=discord.ButtonStyle.green),
        ]

        if commands_desc:
            for _k, _v in commands_desc.items():
                ebd: discord.Embed = discord.Embed(
                    title=_k,
                    description=f"Comandos da cog {_k}",
                )
                for _v_k, _v_v in _v.items():
                    ebd.add_field(
                        name=_v_k,
                        value=_v_v,
                        inline=False,
                    )

                curr_page: pages.Page = pages.Page(embeds=[ebd])

                _pages.append(curr_page)
        else:
            cogs_list: list[discord.Cog] = []

            for cog_n in self.bot.cogs:
                cog: discord.Cog = self.bot.get_cog(cog_n)
                cogs_list.append(cog)

            for _cog in cogs_list:

                ebd: discord.Embed = discord.Embed(
                    title=_cog.qualified_name,
                    description=f"Comandos da cog {_cog.qualified_name}",
                )

                for cmd in _cog.walk_commands():
                    if not cmd.options:
                        opts_str: str = ""
                    else:
                        opts_names: list[str] = []
                        for i in cmd.options:
                            opts_names.append(str(i.name))
                        base_str: str = ", ".join(opts_names)
                        opts_str: str = f": {base_str}"

                    ebd.add_field(
                        name=f"{cmd.name}{opts_str}",
                        value=cmd.description,
                        inline=False,
                    )

                curr_page: pages.Page = pages.Page(embeds=[ebd])

                _pages.append(curr_page)

        paginator: pages.Paginator = pages.Paginator(
            pages=_pages,
            show_indicator=True,
            use_default_buttons=False,
            custom_buttons=buttons,
            loop_pages=True,
            timeout=None,
            custom_view=PersistentView(),
        )

        if not self.bot.persistent_views_added:
            self.bot.add_view(paginator)

            self.bot.persistent_views_added = True


def setup(bot: discord.Bot) -> None:
    """Function that sets up the cog for the bot"""
    bot.add_cog(Generic(bot))
