from pathlib import Path
import json
import urllib.parse

import discord
from discord.ext.commands import Context

__GLOBAL_VERSION = "6.05"
__CN_VERSION = "5.57"

language_alias = {"us": "en", "jp": "ja", "zh": "cn"}


module_dir = Path(__file__).parent
with open(module_dir / "data.json", "r", encoding="utf-8") as f:
    __database = json.load(f)


def get_item_translation(lang, item_name):
    item_name = item_name.lower()
    for item_id in __database.keys():
        data = __database[item_id]
        if lang in data:
            if data[lang].lower() == item_name:
                return item_id, data
    return None


def get_database_link(lang, item_name):
    _item_name = urllib.parse.quote(item_name)
    if lang == "cn":
        return (
            f"https://ff14.huijiwiki.com/wiki/%E7%89%A9%E5%93%81:{_item_name}"
        )
    else:
        return (
            f"https://{lang}.finalfantasyxiv.com/"
            + f"lodestone/playguide/db/search/?q={_item_name}"
        )


async def run(ctx: Context, lang: str, *args: tuple):
    if lang in language_alias:
        lang = language_alias[lang]

    item_id = 0
    item_name = " ".join(args)

    search = get_item_translation(lang, item_name)
    embed_lines = []

    if search is not None:
        (item_id, result) = search
        if "cn" in result:
            if result["cn"] != "":
                _item_name = result["cn"]
                _link = get_database_link("cn", _item_name)
                embed_lines.append(f":flag_cn: [数据库]({_link}) | {_item_name}")

        if "ja" in result:
            if result["ja"] != "":
                _item_name = result["ja"]
                _link = get_database_link("jp", _item_name)
                embed_lines.append(f":flag_jp: [数据库]({_link}) | {_item_name}")

        if "en" in result:
            if result["en"] != "":
                _item_name = result["en"]
                _link = get_database_link("na", _item_name)
                embed_lines.append(f":flag_us: [数据库]({_link}) | {_item_name}")

        if "fr" in result and result["fr"] != "":
            _item_name = result["fr"]
            _link = get_database_link("fr", _item_name)
            embed_lines.append(f":flag_fr: [数据库]({_link}) | {_item_name}")

        if "de" in result:
            if result["de"] != "":
                _item_name = result["de"]
                _link = get_database_link("de", _item_name)
                embed_lines.append(f":flag_de: [数据库]({_link}) | {_item_name}")

    if len(embed_lines) > 0:
        embed = discord.Embed(
            title=f"[物品检索] {item_name} / 匹配到ID: {item_id}",
            description="\n".join(embed_lines),
            color=discord.Colour.blue(),
        )
    else:
        embed = discord.Embed(
            title="物品检索", description="没有找到该物品", color=discord.Colour.red()
        )

    embed.set_footer(text=f"数据信息: 国际服 {__GLOBAL_VERSION}, 中国服 {__CN_VERSION}")
    await ctx.send(embed=embed)
