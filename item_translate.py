import json

with open("item_translation.json", "r", encoding='utf-8') as f:
    database = json.load(f)

def get_item_translation(lang, item_name):
    for item_id in database.keys():
        data = database[item_id]
        if lang in data:
            if data[lang] == item_name:
                return (item_id, data)
    return None