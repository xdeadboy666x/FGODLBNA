import main
import requests
import json
import user
from typing import List, Union

# Define Dracula color palette
dracula_colors = {
    "purple": 0xBD93F9,
    "pink": 0xFF79C6,
    "cyan": 0x8BE9FD,
    "green": 0x50FA7B,
    "yellow": 0xF1FA8C,
    "orange": 0xFFB86C,
}

def topLogin(data: List[Union["user.Rewards", "user.Login", Union["user.Bonus", str]]]) -> None:
    endpoint = main.webhook_discord_url

    rewards: "user.Rewards" = data[0]
    login: "user.Login" = data[1]
    bonus: Union["user.Bonus", str] = data[2]

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
                "title": f"Fate/Grand Order Daily Login Manager - {main.fate_region}",
                "description": f"Login success.\n\n{messageBonus}",
                #"color": dracula_colors["purple"],  # Dracula purple color
                "color": dracula_colors["pink"],  # Dracula pink color
                "fields": [
                    {"name": "Master", "value": f"{name1}", "inline": True},
                    {"name": "ID", "value": f"{fpids1}", "inline": True},
                    {"name": "Level", "value": f"{rewards.level}", "inline": True},
                    {"name": "Summon Ticket", "value": f"{rewards.ticket}", "inline": True},
                    {"name": "Saint Quartz", "value": f"{rewards.stone}", "inline": True},
                    {"name": "Saint Quartz Fragment", "value": f"{rewards.sqf01}", "inline": True},
                    {"name": "Fruit", "value": f"Golden: {rewards.goldenfruit}\nSilver: {rewards.silverfruit}\nBronze: {rewards.bronzefruit}\nBronzed Cobalt: {rewards.bluebronzefruit}", "inline": True},
                    {"name": "Bronze Sapling", "value": f"{rewards.bluebronzesapling}", "inline": True},
                    {"name": "Consecutive / Total Logins", "value": f"{login.login_days} days / {login.total_days} days", "inline": True},
                    {"name": "Pure Prism", "value": f"{rewards.pureprism}", "inline": True},
                    {"name": "FP", "value": f"{login.total_fp}", "inline": True},
                    {"name": "Gained FP", "value": f"+{login.add_fp}", "inline": True},
                    {"name": "Current AP", "value": f"{login.remaining_ap}", "inline": True},
                    {"name": "Holy Grail", "value": f"{rewards.holygrail}", "inline": True},
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

def shop(item: str, quantity: int) -> None:
    endpoint = main.webhook_discord_url

    jsonData = {
        "content": None,
        "embeds": [
            {
                "title": f"Fate/Grand Order Shop Manager - {main.fate_region}",
                "description": "",
                "color": dracula_colors["cyan"],  # Dracula cyan color
                "fields": [
                    {"name": f"Da Vinci's Workshop", "value": f"Used {40 * int(quantity)} AP on x{quantity} {item}", "inline": False}
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

def drawFP(servants: list, missions: list) -> None:
    endpoint = main.webhook_discord_url

    message_mission = ""
    message_servant = ""

    if len(servants) > 0:
        servants_atlas = requests.get(
            "https://api.atlasacademy.io/export/NA/basic_svt.json").json()

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
                "title": f"Fate/Grand Order FP Summon Manager - {main.fate_region}",
                "description": f"{message_mission}",
                "color": dracula_colors["green"],  # Dracula green color
                "fields": [
                    {"name": "FP Gacha results", "value": f"{message_servant}\n", "inline": False}
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
