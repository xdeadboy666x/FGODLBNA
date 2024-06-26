import main
import requests
import user
import json

def topLogin(data: list) -> None:
    endpoint = main.webhook_discord_url

    rewards: user.Rewards = data[0]
    login: user.Login = data[1]
    bonus: user.Bonus or str = data[2]

    with open('login.json', 'r', encoding='utf-8') as f:
        data22 = json.load(f)

        name1 = data22['cache']['replaced']['userGame'][0]['name']
        fpids1 = data22['cache']['replaced']['userGame'][0]['friendCode']

    messageBonus = ''
    nl = '\n'

    if bonus != "No Bonus":
        messageBonus += f"__{bonus.message}__{nl}```{nl.join(bonus.items)}```"

        if bonus.bonus_name is not None:
            messageBonus += f"{nl}__{bonus.bonus_name}__{nl}{bonus.bonus_detail}{nl}```{nl.join(bonus.bonus_camp_items)}```"

        messageBonus += "\n"

    jsonData = {
        "content": None,
        "embeds": [
            {
                "title": f"Fate/Grand Order Login System - {main.fate_region}",
                "description": f"Login success.\n\n{messageBonus}",
                "color": 0xBD93F9,  # Dracula background color
                "fields": [
                    {"name": "Master Name", "value": f"{name1}", "inline": True},
                    {"name": "Friend Code", "value": f"{fpids1}", "inline": True},
                    {"name": "Level", "value": f"{rewards.level}", "inline": True},
                    {"name": "Summon Ticket", "value": f"{rewards.ticket}", "inline": True},
                    {"name": "Saint Quartz", "value": f"{rewards.stone}", "inline": True},
                    {"name": "Saint Quartz Fragment", "value": f"{rewards.sqf01}", "inline": True},
                    {"name": "Golden Fruit", "value": f"{rewards.goldenfruit}", "inline": True},
                    {"name": "Silver Fruit", "value": f"{rewards.silverfruit}", "inline": True},
                    {"name": "Bronze Fruit", "value": f"{rewards.bronzefruit}", "inline": True},
                    {"name": "Bronze Cobalt Fruit", "value": f"{rewards.bluebronzefruit}", "inline": True},
                    {"name": "Bronze Sapling", "value": f"{rewards.bluebronzesapling}", "inline": True},
                    {"name": "Total Login Days", "value": f"{login.login_days} / {login.total_days}", "inline": True},
                    {"name": "Pure Prism", "value": f"{rewards.pureprism}", "inline": True},
                    {"name": "Friend Points", "value": f"{login.total_fp}", "inline": True},
                    {"name": "Friend Points Earned Today", "value": f"+{login.add_fp}", "inline": True},
                    {"name": "Current AP", "value": f"{login.remaining_ap}", "inline": True},
                    {"name": "Holy Grail", "value": f"{rewards.holygrail}", "inline": True},
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo/images/commnet_chara02.png"
                }
            }
        ],
        "attachments": []
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(endpoint, json=jsonData, headers=headers)
    print("topLogin response:", response.status_code, response.text)

def shop(item: str, quantity: int) -> None:
    endpoint = main.webhook_discord_url

    jsonData = {
        "content": None,
        "embeds": [
            {
                "title": f"Bronze Cobalt Fruit Shop - {main.fate_region}",
                "description": "Successful exchange.",
                "color": 0x6272A4,  # Dracula orange color
                "fields": [
                    {"name": "Shop", "value": f"Spent {40 * quantity} AP to purchase {quantity}x {item} (40 AP each)", "inline": False}
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo2/images/commnet_chara10.png"
                }
            }
        ],
        "attachments": []
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(endpoint, json=jsonData, headers=headers)
    print("shop response:", response.status_code, response.text)

def drawFP(servants, missions) -> None:
    endpoint = main.webhook_discord_url

    message_mission = ""
    message_servant = ""

    if len(servants) > 0:
        servants_atlas = requests.get(
            "https://api.atlasacademy.io/export/JP/basic_svt_lang_en.json").json()

        svt_dict = {svt["id"]: svt for svt in servants_atlas}

        for servant in servants:
            svt = svt_dict.get(servant.objectId, None)
            if svt:
                message_servant += f"`{svt['name']}` "

    if len(missions) > 0:
        for mission in missions:
            message_mission += f"__{mission.message}__\n{mission.progressTo}/{mission.condition}\n"

    jsonData = {
        "content": None,
        "embeds": [
            {
                "title": f"Fate/Grand Order FP Summon System - {main.fate_region}",
                "description": f"Completed daily free Friend Point summon. Displaying summon results.\n\n{message_mission}",
                "color": 0x50FA7B,  # Dracula cyan color
                "fields": [
                    {"name": "FP Gacha Results", "value": f"{message_servant}", "inline": False}
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo/images/commnet_chara04_rv.png"
                }
            }
        ],
        "attachments": []
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(endpoint, json=jsonData, headers=headers)
    print("drawFP response:", response.status_code, response.text)
