import discord
from discord.ext import commands
import yaml

import nickname

with open(r'config.yaml') as file:
    bot_config = yaml.load(file, Loader=yaml.FullLoader)

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=bot_config["core"]["command_prefix"], intents=intents)

@bot.command()
async def test(ctx):
    await ctx.send("test")

@bot.command(name="checkname")
async def _check_name(ctx, *args):
    if len(args) == 0:
        message = ":question: 名字输入错误, 格式为 `!checkname Test Name@Anima`"
    else:
        name = " ".join(args)
        print(name)
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
        embed = discord.Embed(title=":loudspeaker: 成员名检测", description="不错哦, 目前服务器中成员都有一个不错的名字", color=discord.Colour.green())
    else:
        embed = discord.Embed(title=":loudspeaker: 成员名检测", description=":x: 检测到了一些不合规的名字", color=discord.Colour.red())
        embed.add_field(name="更改方式", value="1. 在右边的成员列表中找到自己 \n 2. 右键自己 \n 3. 在选单中选择更改昵称", inline=False)
        embed.add_field(name="格式", value="使用 `角色全名@服务器` 的格式, 姓和名开头均为大写的英文字符, 同时 `@` 为英文符号. \n 范例: `Good Name@Chocobo`\n\n 请尽快修改, 机器人自动清理时将会自动踢出不符合规则的成员.", inline=False)

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

@bot.event
async def on_message(message):
    await bot.process_commands(message)

bot.run(bot_config["core"]["discord_token"])