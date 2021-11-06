import aiohttp
import json

__FFLOGS_API_URL = "https://www.fflogs.com/api/v2/client"

__API_TOKEN = None
__TIME_OUT = 10


def init(token, time_out):
    global __API_TOKEN, __TIME_OUT
    __API_TOKEN = token
    __TIME_OUT = time_out


async def fetch(query: dict):
    if __API_TOKEN is None:
        print("[fflogs_api] No API token provided.")
        return None

    payload = json.dumps(
        {"query": str(query).replace("\n", "").replace("\r", "")}
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {__API_TOKEN}",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(__FFLOGS_API_URL, data=payload, headers=headers) as resp:
            if not resp.status == 200:
                print("[fflogs_api] Error: timeout")
            else:
                _data = json.loads(await resp.text())
                if "data" in _data:
                    return _data["data"]
                elif "error" in _data:
                    print("[fflogs_api] Error: {}".format(_data["error"]))
                else:
                    print("[fflogs_api] Error: unknown error")


async def player_info(player_name: str, server: str, region: str = "JP"):
    result = {}
    query = """
    {
        characterData {
            character(name: "%s", serverSlug: "%s", serverRegion: "%s") {
                id
                lodestoneID
                hidden
            }
        }
    }
    """ % (
        player_name,
        server,
        region,
    )
    fflogs_data = await fetch(query)
    if fflogs_data is None:
        return None
    else:
        result = fflogs_data["characterData"]["character"]

    return result


BOSSES = {73: "e9s", 74: "e10s", 75: "e11s", 76: "e12s1", 77: "e12s2"}


async def shb_rankings(player_name: str, server: str, region: str = "JP"):
    result = {}

    patch_codes = {
        "5.0": 1,
        "5.1": 7,
        "5.2": 1,
        "5.3": 7,
        "5.4": 1,
        "5.5": 7,
        "echo": 13,
    }

    # Eden's Promise (e9s - e12s): 38
    for patch in patch_codes:
        query = """
                {
                    characterData {
                        character(name: "%s", serverSlug: "%s", serverRegion: "%s") {
                            zoneRankings(zoneID: 38, partition: %d, difficulty: 101, metric: rdps)
                        }
                    }
                }
                """ % (
            player_name,
            server,
            region,
            patch_codes[patch],
        )

        fflogs_data = await fetch(query)

        if fflogs_data is None:
            return None
        else:
            data = fflogs_data["characterData"]["character"]["zoneRankings"]

            for ranking in data["rankings"]:
                if ranking["totalKills"] > 0:
                    boss_name = BOSSES[ranking["encounter"]["id"]]
                    if (
                        boss_name not in result
                        or result[boss_name]["best"] < ranking["rankPercent"]
                    ):
                        result[boss_name] = {
                            "best": ranking["rankPercent"],
                            "patch": patch,
                        }

    return result
