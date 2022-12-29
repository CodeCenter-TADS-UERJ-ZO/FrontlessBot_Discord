"""Módulo do bot que contém toda a funcionalidade de administração"""


import discord
from discord.ext import commands


#        Carregando  as  regras  aqui  por  enquanto
#   o intuito era  fazer o  bot carregar um JSON com elas
#   mas  lendo a documentação  descobri  que não é  muito
#   recomendado, então enquanto eu não tiver uma database
#   com  sqlite   rodando  para  guardar  as  informações
#   vou ter  que ficar  colocando no  código fonte mesmo.

regras_arr: list[list[str]] = [
    [
        "00. Seja direto nas respostas",
        "Quando alguém tem uma dúvida não é legal ficar de enrolação na hora de responder, então seja direto.",  # pylint: disable=line-too-long
    ],
    [
        "01. Seja MUITO direto nas perguntas",
        "O mesmo vale na hora de perguntar, as pessoas não tem tanto tempo livre, então seja direto na pergunta para receber logo sua respostas e ajudar na resolução de forma efetiva, abaixo estão algumas dicas.",  # pylint: disable=line-too-long
    ],
    [
        "01 A. Não pergunte para perguntar (Don't ask to ask)",
        'Evite coisas como "oi, posso fazer uma pergunta?", "Alguém experiente em XX?", essas perguntas afastam possiveis respostas, além de passarem a imagem de que você quer que resolvam seu problema pra você e não que quer aprender e evoluir.',  # pylint: disable=line-too-long
    ],
    [
        '01 B. Evite o "Problema XY"',
        "Esse problema consiste em perguntar sobre a possível solução ao invés do problema, isso é contra-producente e ineficaz, então por favor, sempre pergunte sobre o problema e nos dê uma precisa e detalhada descrição do mesmo, para mais informações cheque o canal de informações da categoria em questão.",  # pylint: disable=line-too-long
    ],
    [
        '01 C. Sem puro "oi"',
        'Seja direto e não divida a mensagem em varias sub-mensagens, ou seja, sem pressionar enter a cada palavra, você pode demorar um pouco mais para digitar, mas sua pergunta será enviada de uma vez só, ao invés de vir "a prestação".',  # pylint: disable=line-too-long
    ],
    [
        "02. Seja respeitoso",
        "Trate os outros com respeito, aqui é um servidor voltado para programação e interação, e não pra shitposting e ofensas.",  # pylint: disable=line-too-long
    ],
    [
        "03. Sem SPAM",
        "É bastante chato quando voce fica mandando meio milhão de mensagens só pra chamar a atenção, então por favor, sem SPAM.",  # pylint: disable=line-too-long
    ],
    [
        "04. Sem NSFW",
        "Isso é meio óbvio, mas vale ressaltar, sem conteudo NSFW, isso significa, sem gore, pornografia ou conteudos de cunho criminal.",  # pylint: disable=line-too-long
    ],
    [
        "05. Sem auto-promote",
        "Somos abertos a outras comunidades que sejam pertinentes a programação, ou seja, a divulgações pertinentes ao assunto em questão, mas auto-promote não é aceito, tanto no servidor quanto no privado de membros por ser chato. Se você tiver alguma sugestão de algo interessante ao server como um todo, notifique um adminstrador e ele se certificará de adicionar sua contribuição no canal correto.",  # pylint: disable=line-too-long
    ],
    [
        "06. Sem RAID",
        "Sim, enzoGamerXDXD_KKHECKER sem RAIDS aqui, você não vai poder tomar esse servidor.",
    ],
    ["07. Sem ameaça", "   Ninguém gosta de ser ameaçado, então não seja vacilão."],
    ["08. Siga as guidelines do Discord", "Afinal, estamos na plataforma deles."],
    [
        "09. Não divulge informações pessoais",
        "Ninguém aqui quer saber o CPF do seu coleguinha e isso não é engraçado.",
    ],
    [
        "10. Siga as regras dos canais",
        "Veja os fixados, cada canal tem suas regras e sugestões próprias.",
    ],
    [
        "11. Sem pirataria",
        "Qual é, isso pode derrubar o servidor e dar dor de cabeça pra moderação, então sem pirataria.",  # pylint: disable=line-too-long
    ],
    [
        "12. sem @everyone e @here.",
        "Os cargos foram configurados para não poder marcar nenhum desses, mas sempre vale a pena ressaltar.",  # pylint: disable=line-too-long
    ],
    ["13. Tenha bom senso e ética.", "Isso é óbvio."],
]

roles_arr: list[int] = [
    1056704289214578768,  # Python
    1056704334697607241,  # Go
    1056704360937173022,  # JavaScript
    1056704469808713738,  # Java
    1056704503363162206,  # NASM
    1056704647844347984,  # C
]

roles_dict: dict[str, list[int, str]] = {
    "Python": [1056704289214578768, "Python"],
    "Go": [1056704334697607241, "Go"],
    "JavaScript": [1056704360937173022, "JavaScript"],
    "Java": [1056704469808713738, "Java"],
    "NASM": [1056704503363162206, "NASM"],
    "C": [1056704647844347984, "C"],
}

# everyone id: 1002319287308005396


class RoleButton(discord.ui.Button):
    """Classe que implementa a lógica dos botões de cargo."""

    def __init__(self, role: discord.Role) -> None:
        """A button for one role. `custom_id` is needed for persistent views."""
        super().__init__(
            label=role.name,
            style=discord.ButtonStyle.grey,
            custom_id=str(role.id),
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        """Função executada toda vez que o usuário clicar em um botão."""

        user: discord.User | discord.Member | None = interaction.user
        role: discord.Role | None = interaction.guild.get_role(int(self.custom_id))

        if role is None:
            return

        if role not in user.roles:
            await user.add_roles(role)
            await interaction.response.send_message(
                f"added role {role.mention}!", ephemeral=True, delete_after=1.5
            )
        else:
            await user.remove_roles(role)
            await interaction.response.send_message(
                f"removed role {role.mention}", ephemeral=True, delete_after=1.5
            )


class RoleSelect(discord.ui.Select):
    """."""

    def __init__(self) -> None:
        options: list[discord.SelectOption] = []
        for _k, _v in roles_dict.items():
            opt: discord.SelectOption = discord.SelectOption(
                label=_k, value=str(_v[0]), description=_v[1]
            )
            options.append(opt)

        max_val: int = 25 if len(options) > 25 else len(options)
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
        message: discord.Message = interaction.message
        guild: discord.Guild = interaction.guild
        user: discord.User | discord.Member = interaction.user
        dev_role: discord.Role = guild.get_role(1058049513111167016)
        selected_roles: list[discord.Role] = []
        roles_to_add: list[discord.Role] = []
        roles_to_remove: list[discord.Role] = []
        roles_to_add_mentions: list[discord.Role] = []
        roles_to_remove_mentions: list[discord.Role] = []

        for i in self.values:
            role: discord.Role = guild.get_role(int(i))
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

            adding_str: str = f"adicionando cargos: {', '.join(roles_to_add_mentions)}"
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
                ephemeral=True,
                delete_after=5,
            )


class PersistentView(discord.ui.View):
    """."""

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(RoleSelect())


class Adminstrative(commands.Cog):
    """Cog used to manage all Administrative commands"""

    bot_icon_url: str = "https://cdn.discordapp.com/app-icons/1056943227183321118/08902aef3ee87acc3e69081c0a012b71.png?size=2048"  # pylint: disable=line-too-long

    def __init__(self, bot) -> None:
        self.bot = bot
        self.bot.persistent_views_added = False

    @commands.slash_command(name="regras", description="Exibe as regras")
    @commands.has_role(1056755317419028560)
    async def regras(self, ctx: discord.ApplicationContext) -> None:
        """Função que exibe as regras do servidor"""

        embed: discord.Embed = discord.Embed(
            title="Regras",
            description="Estas são as regras do servidor.",
            color=discord.Colour.light_grey(),
        )
        embed.add_field(name=regras_arr[0][0], value=regras_arr[0][1], inline=False)
        embed.add_field(name=regras_arr[1][0], value=regras_arr[1][1], inline=False)
        embed.add_field(name=regras_arr[2][0], value=regras_arr[2][1], inline=False)
        embed.add_field(name=regras_arr[3][0], value=regras_arr[3][1], inline=False)
        embed.add_field(name=regras_arr[4][0], value=regras_arr[4][1], inline=False)
        embed.add_field(name=regras_arr[5][0], value=regras_arr[5][1], inline=False)
        embed.add_field(name=regras_arr[6][0], value=regras_arr[6][1], inline=False)
        embed.add_field(name=regras_arr[7][0], value=regras_arr[7][1], inline=False)
        embed.add_field(name=regras_arr[8][0], value=regras_arr[8][1], inline=False)
        embed.add_field(name=regras_arr[9][0], value=regras_arr[9][1], inline=False)
        embed.add_field(name=regras_arr[10][0], value=regras_arr[10][1], inline=False)
        embed.add_field(name=regras_arr[11][0], value=regras_arr[11][1], inline=False)
        embed.add_field(name=regras_arr[12][0], value=regras_arr[12][1], inline=False)
        embed.add_field(name=regras_arr[13][0], value=regras_arr[13][1], inline=False)
        embed.add_field(name=regras_arr[14][0], value=regras_arr[14][1], inline=False)
        embed.add_field(name=regras_arr[15][0], value=regras_arr[15][1], inline=False)
        embed.add_field(name=regras_arr[16][0], value=regras_arr[16][1], inline=False)

        embed.set_author(name="Frontless Programming", icon_url=self.bot_icon_url)
        embed.set_thumbnail(url=self.bot_icon_url)
        embed.set_footer(
            text="Feito pela comunidade com ❤️.", icon_url=self.bot_icon_url
        )

        await ctx.respond(embed=embed)

    @commands.slash_command(name="select_langs_button", description="test_langs")
    @commands.has_role(1056755317419028560)
    async def langs(self, ctx: discord.ApplicationContext) -> None:
        """Itera sob a array de cargos e gera botões para cada um deles"""
        view: discord.ui.View = discord.ui.View(timeout=None)

        for role_id in roles_arr:
            role: discord.Role | None = ctx.guild.get_role(role_id)
            view.add_item(RoleButton(role))

        await ctx.respond("clique no cargo desejado", view=view)

    @commands.slash_command(
        name="language_selection",
        description="Displays the dropdown for the language selection",
    )
    @commands.has_role(1056755317419028560)
    async def language_selection(self, ctx: discord.ApplicationContext) -> None:
        """Displays the dropdown for the language selection"""

        if ctx.message:
            await ctx.edit(view=PersistentView())
        else:
            await ctx.respond(view=PersistentView())

    @commands.slash_command(
        name="create_category",
        description="Cria uma categoria, os cargos e configura todos os canais",
    )
    @commands.has_role(1056755317419028560)
    async def create_category(self, ctx: discord.ApplicationContext) -> None:
        """Comando de gerenciamento de categorias, especifico para as categorias de linguagem
        tem como argumento o nome da linguagem em questão e cria todos os canais base da categoria
        além de criar o cargo e configurar as permissões."""

        await ctx.respond("Implementação em progresso...")

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.MissingRole):
            await ctx.send(
                f"Permissão negada {ctx.author.name} esse comando só pode ser usado por um administrador.",  # pylint: disable=line-too-long
                reference=ctx.message,
                delete_after=4,
            )
        else:
            raise error  # Here we raise other errors to ensure they aren't ignored

    @commands.slash_command(name="welcome", description="Exibe a tela de boas-vindas")
    @commands.has_role(1056755317419028560)
    async def welcome(self, ctx: discord.ApplicationContext) -> None:
        """."""

        rule_channel: discord.TextChannel = ctx.guild.get_channel(1056738639813546034)
        embed: discord.Embed = discord.Embed(
            title="Bem-vindo(a)",
            color=discord.Colour.light_grey(),
        )
        embed.add_field(
            name="Leia-me",
            value=f"Nessa comunidade programadores se reunem para conversar, estudar e interagir entre si. Recomendo dar uma lida nas {rule_channel.mention} para ter certeza de que você não vai levar um timeout por engano.\n\n**Siga as instruções abaixo para ter acesso ao servidor**\n",  # pylint: disable=line-too-long
            inline=False,
        )
        embed.set_author(name="Frontless Programming")
        embed.set_thumbnail(url=self.bot_icon_url)
        embed.set_footer(
            text="Um abraço da FrontlessTeam. ❤️.", icon_url=self.bot_icon_url
        )
        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Listener para reativar os botões ao iniciar do bot"""
        if not self.bot.persistent_views_added:
            self.bot.add_view(PersistentView())

            view: discord.ui.View = discord.ui.View(timeout=None)
            guild: discord.Guild = self.bot.get_guild(1002319287308005396)
            for role_id in roles_arr:
                role: discord.Role | None = guild.get_role(role_id)
                view.add_item(RoleButton(role))

            self.bot.add_view(view)
            self.bot.persistent_views_added = True


def setup(bot) -> None:
    """Function that sets up the cog for the bot"""
    bot.add_cog(Adminstrative(bot))
