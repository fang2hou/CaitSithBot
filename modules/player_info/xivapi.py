import aiohttp
import json

__XIVAPI_URL = "https://xivapi.com"

__API_TOKEN = None
__TIME_OUT = 10


def init(token, time_out):
    global __API_TOKEN, __TIME_OUT
    __API_TOKEN = token
    __TIME_OUT = time_out


async def fetch(query: str):
    access_point = __XIVAPI_URL + query + "?private_key=" + __API_TOKEN

    headers = {
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(access_point, headers=headers) as resp:
            if resp.status == 200:
                _data = json.loads(await resp.text())
                if "Character" in _data:
                    return _data
                elif "Error" in _data and "Message" in _data:
                    print("[xivapi] Error: {}".format(_data["Message"]))
                    print(_data)
                else:
                    print("[xivapi] Error: unknown error")
                    return _data


async def lodestone_info(lodestone_id: int):
    return await fetch("/character/{}".format(lodestone_id))
