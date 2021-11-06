from os import name
from . import fflogs
from . import xivapi

import re
import discord


def init(config):
    fflogs.init(config["fflogs_token"], config["time_out"])
    xivapi.init(config["xivapi_token"], config["time_out"])


async def send_usage_of_player_info(ctx):
    await ctx.send("玩家信息查询方式: `!playerinfo <player name> <server>`")


async def send_xivapi_error(ctx):
    await ctx.send(ctx.author.mention + "Lodestone 访问超时, 请稍后再试!")


async def send_no_player(ctx):
    await ctx.send("FFLogs 查无此人!")


name_server = re.compile(
    r"([^ @]* [^ @]*)[ @-](anima|asura|belias|chocobo|hades|ixion|mandragora|masamune|pandaemonium|shinryu|titan)"
)
server_name = re.compile(
    r"(anima|asura|belias|chocobo|hades|ixion|mandragora|masamune|pandaemonium|shinryu|titan)[ @-]([^ @]* [^ @]*)"
)


def parse_name(full_name):
    full_name = full_name.lower()
    result = name_server.findall(full_name)

    if result:
        return result[0][0], result[0][1]
    else:
        result = server_name.findall(full_name)
        if result:
            return result[0][1], result[0][0]

    return None


def generate_line_of_ranking(embed, ranking_data, boss_index, boss_name):
    if boss_index not in ranking_data:
        embed.add_field(
            name="<:ffxiv_icon_boss:865082385489068043> " + boss_name,
            value="无战斗数据",
            inline=True,
        )
        return

    _best_percent = float(ranking_data[boss_index]["best"])
    _patch_name = ranking_data[boss_index]["patch"]
    if _patch_name == "echo":
        _patch_name = "5.55"

    embed.add_field(
        name="<:ffxiv_icon_boss:865082385489068043> " + boss_name,
        value="**{:.1f}** ({})".format(_best_percent, _patch_name),
        inline=True,
    )


class_emoji = {
    1: "<:ffxiv_class_pld:865082878277976075>",
    3: "<:ffxiv_class_war:865082878210605116>",
    32: "<:ffxiv_class_drk:865082878181244949>",
    37: "<:ffxiv_class_gnb:865082878211915786>",
    2: "<:ffxiv_class_mnk:865082878282170378>",
    4: "<:ffxiv_class_drg:865082878269587476>",
    29: "<:ffxiv_class_nin:865082878357274644>",
    34: "<:ffxiv_class_sam:865082878265655296>",
    6: "<:ffxiv_class_whm:865082878558863410>",
    28: "<:ffxiv_class_sch:865082877950951476>",
    33: "<:ffxiv_class_ast:865082877871783937>",
    5: "<:ffxiv_class_brd:865082877971529769>",
    31: "<:ffxiv_class_mch:865082877870604290>",
    38: "<:ffxiv_class_dnc:865082878575247360>",
    7: "<:ffxiv_class_blm:865082878228299806>",
    26: "<:ffxiv_class_smn:865082877929979905>",
    35: "<:ffxiv_class_rdm:865082877867458623>",
    36: "<:ffxiv_class_blu:865082878235770910>",
}


def get_class_level_string(class_level_list, ids):
    result = []
    for id in ids:
        emoji = class_emoji[id]
        if id == 28:  # scholar
            id = 26
        level = class_level_list[id]
        if id in class_level_list:
            if level == 80 or level == 70 and id == 36:
                _level = f"**{level}**"
            else:
                _level = f"{level}"

            if level < 10:
                _level += " "

            result.append(emoji + " " + _level)

    _result = ""
    for i in range(len(result)):
        if i != 0:
            if i % 2 == 0:
                _result += "\n"
            else:
                _result += " "
        _result += result[i]

    return _result


async def player_info(ctx, *args):
    character_name = None
    server = None

    if len(args) == 0:
        full_name = ctx.author.nick
    else:
        full_name = " ".join(args)
        full_name = full_name.replace("`", "")

    _parsed_name = parse_name(full_name)
    if not _parsed_name:
        await send_usage_of_player_info(ctx)
        return
    else:
        character_name = _parsed_name[0]
        server = _parsed_name[1]

    player_info = await fflogs.player_info(character_name, server)
    if not player_info:
        await send_no_player(ctx)
        return

    attempt_times = 0
    while attempt_times < 10:
        lodestone_info = await xivapi.lodestone_info(player_info["lodestoneID"])
        if lodestone_info:
            break
        else:
            attempt_times += 1

    shb_rankings = await fflogs.shb_rankings(character_name, server)

    embed_data = {}
    embed_data["title"] = "<:ffxiv_icon_info:864598480730325002> 玩家信息"

    embed = discord.Embed(**embed_data)

    if lodestone_info:
        embed.set_author(
            name=character_name.title() + "@" + server.title(),
            url="https://jp.finalfantasyxiv.com/lodestone/character/{}/".format(
                player_info["lodestoneID"]
            ),
            icon_url=lodestone_info["Character"]["Avatar"],
        )

        embed.add_field(
            name="部队",
            value=lodestone_info["Character"]["FreeCompanyName"],
            inline=True,
        )

        eureka_level = lodestone_info["Character"]["ClassJobsElemental"][
            "Level"
        ]
        if not eureka_level or eureka_level == 0:
            eureka_level = "还未前往禁地"
        else:
            eureka_level = "等级 " + str(eureka_level)

        embed.add_field(name="优雷卡", value=eureka_level, inline=True)

        bozjan_level = lodestone_info["Character"]["ClassJobsBozjan"]["Level"]
        if not bozjan_level or bozjan_level == 0:
            bozjan_level = "未参加义军"
        else:
            bozjan_level = "等级 " + str(bozjan_level)

        embed.add_field(name="博兹雅", value=bozjan_level, inline=True)

        class_level_list = {}
        for class_info in lodestone_info["Character"]["ClassJobs"]:
            if class_info["ClassID"] in class_emoji:
                class_level_list[class_info["ClassID"]] = class_info["Level"]

        embed.add_field(
            name="坦克",
            value=get_class_level_string(class_level_list, [1, 3, 32, 37]),
            inline=True,
        )
        embed.add_field(
            name="治疗",
            value=get_class_level_string(class_level_list, [6, 28, 33]),
            inline=True,
        )
        embed.add_field(
            name="近战",
            value=get_class_level_string(class_level_list, [2, 4, 29, 34]),
            inline=True,
        )
        embed.add_field(
            name="远敏",
            value=get_class_level_string(class_level_list, [5, 31, 38]),
            inline=True,
        )
        embed.add_field(
            name="魔法",
            value=get_class_level_string(class_level_list, [7, 26, 35, 36]),
            inline=True,
        )

    if player_info["hidden"]:
        embed.add_field(
            name="FFLogs 亮眼表现",
            value="该玩家已隐藏自己的排名数据.",
            inline=True,
        )
    else:
        fflog_url_base = "https://www.fflogs.com/character/id/{}".format(
            player_info["id"]
        )

        embed.add_field(
            name="<:ffxiv_icon_info:864598480730325002> FFLogs 亮眼表现",
            value="[5.4]({})".format(fflog_url_base + "#partition=1")
            + " | "
            + "[5.5]({})".format(fflog_url_base + "#partition=7")
            + " | "
            + "[5.55]({})".format(fflog_url_base + "#partition=13"),
            inline=False,
        )

        generate_line_of_ranking(embed, shb_rankings, "e9s", "暗黑之云 | E9S")
        generate_line_of_ranking(embed, shb_rankings, "e10s", "影之王 | E10S")
        generate_line_of_ranking(embed, shb_rankings, "e11s", "绝命战士 | E11S")
        generate_line_of_ranking(embed, shb_rankings, "e12s1", "伊甸之约 | E12S门神")
        generate_line_of_ranking(embed, shb_rankings, "e12s2", "暗之巫女 | E12S本体")

    await ctx.send(embed=embed)
