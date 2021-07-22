import json
import urllib.parse

with open("item_translation.json", "r", encoding='utf-8') as f:
    database = json.load(f)

def get_item_translation(lang, item_name):
    for item_id in database.keys():
        data = database[item_id]
        if lang in data:
            if data[lang] == item_name:
                return (item_id, data)
    return None

def get_database_link(lang, item_name):
    if lang == "cn":
        return f"https://ff14.huijiwiki.com/wiki/%E7%89%A9%E5%93%81:{urllib.parse.quote(item_name)}"
    else:
        return f"https://{lang}.finalfantasyxiv.com/lodestone/playguide/db/search/?q={urllib.parse.quote(item_name)}" 