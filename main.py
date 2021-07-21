import discord
from discord.ext import commands
from discord.ext.commands.core import check
import yaml

import nickname
import item_translate

with open(r'config.yaml') as file:
    bot_config = yaml.load(file, Loader=yaml.FullLoader)

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(
    command_prefix=bot_config["core"]["command_prefix"], intents=intents)


@bot.command()
async def test(ctx):
    await ctx.send("test")


@bot.command(name="is")
async def _itemsearch(ctx, lang, *args):
    item_name = " ".join(args)
    (id, result) = item_translate.get_item_translation(lang, item_name)

    desc = []
    if result is not None:
        if "cn" in result:
            if result["cn"] != "":
                desc.append(":flag_cn:  " + result["cn"])

        if "ja" in result:
            if result["ja"] != "":
                desc.append(":flag_jp:  " + result["ja"])

        if "en" in result:
            if result["ja"] != "":
                desc.append(":flag_us:  " + result["en"])

        if "fr" in result:
            if result["ja"] != "":
                desc.append(":flag_fr:  " + result["fr"])

        if "de" in result:
            if result["de"] != "":
                desc.append(":flag_de:  " + result["de"])

    if len(desc) > 0:
        embed = discord.Embed(title="物品检索 [" + id + "]", description="\n".join(
            desc), color=discord.Colour.blue())
    else:
        embed = discord.Embed(
            title="物品检索", description="没有找到该物品", color=discord.Colour.red())

    embed.set_footer(text="数据信息: 国际服 5.58, 中国服 5.45")
    await ctx.send(embed=embed)


@bot.command(name="checkname")
async def _check_name(ctx, *args):
    if len(args) == 0:
        message = ":question: 名字输入错误, 格式为 `!checkname Test Name@Anima`"
    else:
        name = " ".join(args)
        name = name.replace('`', '')
        result = nickname.is_vaild_nickname(name)
        if result:
            message = ":white_check_mark: 恭喜您, 该名字符合条件."
        else:
            message = ":question: 这名字看上去不太对哦, 请再次确认格式为 `游戏角色名@服务器名`!"

    await ctx.send(message)


@bot.command(name="checknick")
async def check_nicknames(ctx, *args):
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
        if not nickname.is_vaild_nickname(name):
            badboys.append(member)

    if len(badboys) == 0:
        embed = discord.Embed(title=":loudspeaker: 成员名检测",
                              description="不错哦, 目前服务器中成员都有一个不错的名字", color=discord.Colour.green())
    else:
        embed = discord.Embed(title=":loudspeaker: 成员名检测",
                              description=":x: 检测到了一些不合规的名字", color=discord.Colour.red())
        embed.add_field(
            name="更改方式", value="1. 在右边的成员列表中找到自己 \n 2. 右键自己 \n 3. 在选单中选择更改昵称", inline=False)
        embed.add_field(
            name="格式", value="使用 `角色全名@服务器` 的格式, 姓和名开头均为大写的英文字符, 同时 `@` 为英文符号. \n 范例: `Good Name@Chocobo`\n\n 请尽快修改, 机器人自动清理时将会自动踢出不符合规则的成员.", inline=False)

        for badboy in badboys:
            if badboy.nick is None:
                nick = "(未设定)"
            else:
                nick = badboy.nick

            embed.add_field(name=nick, value=f"{badboy.mention}")

    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))


async def check_user_nickname(member):
    if member.bot:
        return

    name = member.nick
    if name is None:
        name = member.name
    if not nickname.is_vaild_nickname(name):
        embed = discord.Embed(title=":x: 成员名检测",
                              description=":radio_button: 我检测到了你的名字不符合本服务器的规则哦~", color=discord.Colour.red())
        embed.add_field(
            name=":small_orange_diamond: 更改方式", value="1. 在服务器右侧的成员列表中找到自己 \n 2. 右键自己 \n 3. 在选单中选择更改昵称", inline=False)
        embed.add_field(
            name=":small_orange_diamond: 格式", value="使用 `角色全名@服务器` 的格式, 姓和名开头均为大写的英文字符, 同时 `@` 为英文符号. 范例: `Good Name@Chocobo`\n\n 使用命令 `!checkname Good Name@Chocobo` 这样可以测试是否符合规则.\n 请尽快修改, 机器人自动清理时将会自动踢出不符合规则的成员.", inline=False)

        await member.send("我来自 FFXIV Mana 服务器! https://discord.gg/3G3VN3RZwv", embed=embed)


@bot.event
async def on_message(message):
    if not message.channel.type == discord.ChannelType.private:
        await check_user_nickname(message.author)
    await bot.process_commands(message)

bot.run(bot_config["core"]["discord_token"])
