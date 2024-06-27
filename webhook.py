import main
import requests
import user
import json
from typing import Union

# Define Dracula color palette
dracula_colors = {
    "purple": 0xBD93F9,
    "pink": 0xFF79C6,
    "cyan": 0x8BE9FD,
    "green": 0x50FA7B,
    "yellow": 0xF1FA8C,
    "orange": 0xFFB86C,
}

def topLogin(data: list) -> None:
    endpoint = main.webhook_discord_url

    rewards: user.Rewards = data[0]
    login: user.Login = data[1]
    bonus: Union[user.Bonus, str] = data[2]

    with open('login.json', 'r', encoding='utf-8') as f:
        data22 = json.load(f)

    name1 = data22['cache']['replaced']['userGame'][0]['name']
    fpids1 = data22['cache']['replaced']['userGame'][0]['friendCode']
    
    # Extract svt and ce data
    svtCount = 0
    ceCount = 0
    for svt in data22['cache']['replaced']['userSvt']:
        if str(svt['svtId']).startswith('93') or str(svt['svtId']).startswith('94') or str(svt['svtId']).startswith('98'):
            ceCount += 1
        else:
            svtCount += 1
    messageBonus = ''
    nl = '\n'

    if isinstance(bonus, user.Bonus):
        messageBonus += f"__{bonus.message}__{nl}```{nl.join(bonus.items)}```"

        if bonus.bonus_name is not None:
            messageBonus += f"{nl}__{bonus.bonus_name}__{nl}{bonus.bonus_detail}{nl}```{nl.join(bonus.bonus_camp_items)}```"

        messageBonus += "\n"
    elif isinstance(bonus, str) and bonus != "No Bonus":
        messageBonus += f"{bonus}\n"

    jsonData = {
        "content": None,
        "embeds": [
            {
                "title": f"Fate/Grand Order Login System - {main.fate_region}",
                "description": f"Login success.\n\n{messageBonus}",
                "color": dracula_colors["pink"],  # Dracula pink color
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
                    {"name": "FP", "value": f"{login.total_fp}", "inline": True},
                    {"name": "Gained FP", "value": f"+{login.add_fp}", "inline": True},
                    {"name": "Holy Grail", "value": f"{rewards.holygrail}", "inline": True},
                    # Add svt and ce data to the fields
                    {"name": "Servants", "value": f"{svtCount}", "inline": True},
                    {"name": "Craft Essences", "value": f"{ceCount}", "inline": True},
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo3/images/commnet_chara16.png"
                }
            }
        ],
        "attachments": []
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(endpoint, json=jsonData, headers=headers)
    print("topLogin response:", response.status_code, response.text)

# Example usage with svt and ce counts
data = [...]  # Replace with actual data list
svt_count = 0  # Replace with actual servant count
ce_count = 0  # Replace with actual craft essence count
topLogin(data, svt_count, ce_count)

def shop(item: str, quantity: str) -> None:
    endpoint = main.webhook_discord_url

    jsonData = {
        "content": None,
        "embeds": [
            {
                "title": f"Bronze Cobalt Fruit Shop - {main.fate_region}",
                "description": f"Successful exchange.",
                "color": dracula_colors["cyan"],  # Dracula cyan color
                "fields": [
                    {"name": f"Shop", "value": f"Spent {40 * int(quantity)} AP to purchase {quantity}x {item} (40 AP each)", "inline": False}
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo3/images/commnet_chara10.png"
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

    # Assuming data is loaded here similar to topLogin
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    svtCount = 0
    ceCount = 0
    for svt in data['cache']['replaced']['userSvt']:
        if str(svt['svtId']).startswith('93') or str(svt['svtId']).startswith('94') or str(svt['svtId']).startswith('98'):
            ceCount += 1
        else:
            svtCount += 1

    if len(servants) > 0:
        servants_atlas = requests.get(
            f"https://api.atlasacademy.io/export/NA/nice_servant.json").json()

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
                "description": f"Gacha results.\n\n{message_mission}",
                "color": dracula_colors["green"],  # Dracula green color
                "fields": [
                    {"name": "FP Gacha results", "value": f"{message_servant}", "inline": False}
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo3/images/commnet_chara04.png"
                }
            }
        ],
        "attachments": []
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(endpoint, json=jsonData, headers=headers)
    print("drawFP response:", response.status_code, response.text)
def shop(item: str, quantity: str) -> None:
    endpoint = main.webhook_discord_url
    
    jsonData = {
        "content": None,
        "embeds": [
            {
                "title": f"Bronze Cobalt Fruit Shop - {main.fate_region}",
                "description": f"Successful exchange.",
                "color": dracula_colors["cyan"],  # Dracula cyan color
                "fields": [
                    {"name": f"Shop", "value": f"Spent {40 * int(quantity)} AP to purchase {quantity}x {item} (40 AP each)", "inline": False}
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo3/images/commnet_chara10.png"
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

    # Assuming data is loaded here similar to topLogin
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    svtCount = 0
    ceCount = 0
    for svt in data['cache']['replaced']['userSvt']:
        if str(svt['svtId']).startswith('93') or str(svt['svtId']).startswith('94') or str(svt['svtId']).startswith('98'):
            ceCount += 1
        else:
            svtCount += 1

    if len(servants) > 0:
        servants_atlas = requests.get(
            f"https://api.atlasacademy.io/export/NA/nice_servant.json").json()

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
                "description": f"Gacha results.\n\n{message_mission}",
                "color": dracula_colors["green"],  # Dracula green color
                "fields": [
                    {"name": "FP Gacha results", "value": f"{message_servant}", "inline": False}
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo3/images/commnet_chara04.png"
                }
            }
        ],
        "attachments": []
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(endpoint, json=jsonData, headers=headers)
    print("drawFP response:", response.status_code, response.text)
