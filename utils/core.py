import discord

__bot_config = None


def init(config):
    global __bot_config
    __bot_config = config


def is_support_channel(ctx):
    _id = None
    if type(ctx) is discord.channel.TextChannel:
        _id = ctx.id
    elif type(ctx) is discord.message.Message:
        _id = ctx.channel.id
    else:
        _id = str(ctx)
    return _id in __bot_config["core"]["support_channel_ids"]


def is_admin(ctx):
    _id = None
    if type(ctx) is discord.member.Member:
        _id = ctx.id
    else:
        _id = str(ctx)
    return _id in __bot_config["core"]["admin_ids"]
