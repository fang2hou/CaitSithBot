import re
import discord

regex = r"^[A-Z][^ @]* [A-Z][^ @]*@(Anima|Asura|Belias|Chocobo|Hades|Ixion|Mandragora|Masamune|Pandaemonium|Shinryu|Titan)$"
checker = re.compile(regex)


def is_vaild_nickname(nickname) -> bool:
    matches = checker.match(nickname)
    if matches is None:
        return False
    else:
        return True


async def check_name(ctx, *args):
    if len(args) == 0:
        message = ":question: 名字输入错误, 格式为 `!checkname Test Name@Anima`!\n> 如果发现总是@到别人, 建议采用 \` 符号进行包裹."
    else:
        name = " ".join(args)
        name = name.replace("`", "")
        result = is_vaild_nickname(name)
        if result:
            message = ":white_check_mark: 恭喜您, 该名字符合条件."
        else:
            message = ":question: 这名字看上去不太对哦, 请再次确认格式为 `游戏角色名@服务器名`!\n> 如果发现总是@到别人, 建议采用 \` 符号进行包裹."

    await ctx.send(message)


async def check_member_name(member):
    if member.bot:
        return

    name = member.nick
    if name is None:
        name = member.name
    if not is_vaild_nickname(name):
        embed = discord.Embed(
            title=":x: 成员名检测",
            description=":radio_button: 我检测到了你的名字不符合本服务器的规则哦~",
            color=discord.Colour.red(),
        )
        embed.add_field(
            name=":small_orange_diamond: 更改方式",
            value="1. 在服务器右侧的成员列表中找到自己 \n 2. 右键自己 \n 3. 在选单中选择更改昵称",
            inline=False,
        )
        embed.add_field(
            name=":small_orange_diamond: 格式",
            value="使用 `角色全名@服务器` 的格式, 姓和名开头均为**大写的英文字符**, 同时 `@` 为英文符号. 范例: `Good Name@Chocobo`\n\n 使用命令 `!checkname Good Name@Chocobo` 这样可以测试是否符合规则. (命令在私聊, 服务器中都可以使用)\n 请尽快修改, 机器人自动清理时将会自动踢出不符合规则的成员.",
            inline=False,
        )

        await member.send(
            "我来自 FFXIV Mana 服务器! https://discord.gg/3G3VN3RZwv", embed=embed
        )


async def check_all_member_names(ctx):
    guild = ctx.guild
    if guild is None:
        return

    badboys = []
    for member in guild.members:
        if member.bot:
            continue
        name = member.nick
        if name is None:
            name = member.name
        if not is_vaild_nickname(name):
            badboys.append(member)

    if len(badboys) == 0:
        embed = discord.Embed(
            title=":loudspeaker: 成员名检测",
            description="不错哦, 目前服务器中成员都有一个不错的名字",
            color=discord.Colour.green(),
        )
    else:
        embed = discord.Embed(
            title=":loudspeaker: 成员名检测",
            description=":x: 检测到了一些不合规的名字",
            color=discord.Colour.red(),
        )
        embed.add_field(
            name="更改方式",
            value="1. 在右边的成员列表中找到自己 \n 2. 右键自己 \n 3. 在选单中选择更改昵称",
            inline=False,
        )
        embed.add_field(
            name="格式",
            value="使用 `角色全名@服务器` 的格式, 姓和名开头均为大写的英文字符, 同时 `@` 为英文符号. \n 范例: `Good Name@Chocobo`\n\n 请尽快修改, 机器人自动清理时将会自动踢出不符合规则的成员.",
            inline=False,
        )

        for badboy in badboys:
            if badboy.nick is None:
                nick = "(未设定)"
            else:
                nick = badboy.nick

            embed.add_field(name=nick, value=f"{badboy.mention}")

    await ctx.send(embed=embed)
