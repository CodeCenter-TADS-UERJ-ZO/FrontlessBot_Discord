"""Cog that contains all adminstrative commands"""


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


class SelectRoles(discord.ui.View):
    """custom view"""

    opts: list[discord.SelectOption] = [
        discord.SelectOption(label="Go", description="Go", value="Go"),
        discord.SelectOption(label="C", description="C", value="C"),
        discord.SelectOption(label="Python", description="Python", value="Python"),
        discord.SelectOption(label="Java", description="Java", value="Java"),
        discord.SelectOption(
            label="JavaScript", description="JavaScript", value="JavaScript"
        ),
        discord.SelectOption(label="NASM", description="NASM", value="NASM"),
    ]

    @discord.ui.select(
        placeholder="Selecione suas linguagens",
        min_values=1,
        max_values=6,
        options=opts,
    )
    async def select_callback(self, select, interaction):
        """callback function"""
        roles_dict: dict[str, int] = {
            "Python": 1056704289214578768,
            "Go": 1056704334697607241,
            "JavaScript": 1056704360937173022,
            "Java": 1056704469808713738,
            "NASM": 1056704503363162206,
            "C": 1056704647844347984,
        }

        user = interaction.user
        for i in select.values:
            if i in roles_dict:
                print(f"{i}:{roles_dict[i]}")
                role = interaction.guild.get_role(roles_dict[i])
                # await interaction.user.add_roles(role)
                if role not in user.roles:
                    await user.add_roles(role)
                    await interaction.response.send_message(
                        f"Cargos adicionados {user.mention}",
                        ephemeral=True,
                    )
                else:
                    await user.remove_roles(role)
                    await interaction.response.send_message(
                        f"Cargos removidos {user.mention}",
                        ephemeral=True,
                    )

        await interaction.response.send_message("pronto!", ephemeral=True)

    #             IMPLEMENTAÇÃO AINDA NÃO SUPORTADA
    #   Enquanto   lia   a   API   descobri   a   role_select
    #   que  gera  um  menu  baseado nos  cargos do  servidor
    #   porém, ela é bem recente e não existe opção de filtro
    #   e   nem   o   py-cord   implementa   ela    muito bem
    #   então optei por usar o  "modo antigo"  pelo  controle
    #   mas  quis  salvar  essa implementação para uma futura
    #   atualização no código do bot.
    #
    # @discord.ui.select(
    #     select_type=discord.ComponentType.role_select,
    #     placeholder="Selecione suas linguagens",
    #     min_values=1,
    #     max_values=25,
    # )
    # async def select_callback(self, select, interaction):
    #     """callback function"""
    #     for i in select.values:
    #         await interaction.user.add_roles(i)
    #     await interaction.response.send_message("pronto!")


class Adminstrative(commands.Cog):
    """Cog used to manage all Administrative commands"""

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(name="regras", description="Exibe as regras")
    async def regras(self, ctx: discord.ApplicationContext) -> None:
        """function that executes when a user uses de /hello command"""
        icon_url: str = "https://cdn.discordapp.com/app-icons/1056943227183321118/08902aef3ee87acc3e69081c0a012b71.png?size=2048"  # pylint: disable=line-too-long

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

        embed.set_author(name="Frontless Programming", icon_url=icon_url)
        embed.set_thumbnail(url=icon_url)
        embed.set_footer(text="Feito pela comunidade com ❤️.", icon_url=icon_url)

        await ctx.respond(embed=embed)

    @commands.slash_command(name="test_langs", description="test_langs")
    async def langs(self, ctx: discord.ApplicationContext) -> None:
        """langs"""
        await ctx.send("Selecione uma linguagem", view=SelectRoles(timeout=None))


def setup(bot) -> None:
    """Function that sets up the cog for the bot"""
    bot.add_cog(Adminstrative(bot))