import discord
from discord.ext import commands

import yaml

import utils
import utils.message

import modules.player_info as player_info
import modules.item_search as item_search
import modules.name_check as name_check

with open(r"config.yaml", encoding="utf8") as file:
    bot_config = yaml.load(file, Loader=yaml.FullLoader)

utils.init(bot_config)

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(
    command_prefix=bot_config["core"]["command_prefix"],
    intents=intents,
    activity=discord.Activity(
        name=bot_config["core"]["watching"], type=discord.ActivityType.watching
    ),
)

player_info.init(bot_config["player_info"])


# 玩家资料
@bot.command(name="playerinfo", aliases=["pi", "player_info"])
async def _player_info(ctx, *args):
    if ctx.channel.id in bot_config["player_info"]["channel_blacklist"]:
        await ctx.send("请前往 <#867239258123927582> 频道进行该命令的使用.")
        return
    await player_info.player_info(ctx, *args)


# 物品搜索
@bot.command(
    name="itemsearch",
    aliases=["is", "si", "item_search", "search_item", "isearch"],
)
async def _(ctx, lang, *args):
    await item_search.run(ctx, lang, *args)


# 名字检查
@bot.command(
    name="checkname",
    aliases=["cn", "nc", "check_name", "namecheck", "name_check"],
)
async def _check_name(ctx, *args):
    await name_check.check_name(ctx, *args)


# 全员名字检查(需要管理员权限)
@bot.command(name="checkallnames")
async def _check_all_member_names(ctx):
    if utils.is_admin(ctx.author):
        await name_check.check_all_member_names(ctx)
    else:
        await utils.message.send_error_message(
            ctx, "全员名字检查", "抱歉, 您没有权限使用此命令.\n请联系机器人开发管理员."
        )


@bot.event
async def on_ready():
    print("Logged on as {0}!".format(bot.user))


@bot.event
async def on_message(message):
    if not message.channel.type == discord.ChannelType.private:
        # 公开频道发言检测
        if bot_config["name_check"]["always"]:
            if (
                not utils.is_support_channel(message)
                or bot_config["name_check"]["run_on_support_channel"]
            ):
                await name_check.check_member_name(message.author)

    await bot.process_commands(message)


bot.run(bot_config["core"]["discord_token"])
