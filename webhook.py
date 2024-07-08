import requests
import json
from typing import Union, List
import main
import user

# Define Dracula color palette
dracula_colors = {
    "purple": 0xBD93F9,
    "pink": 0xFF79C6,
    "cyan": 0x8BE9FD,
    "green": 0x50FA7B,
    "yellow": 0xF1FA8C,
    "orange": 0xFFB86C,
}

def top_login(data: List[Union[user.Rewards, user.Login, Union[user.Bonus, str]]]) -> None:
    """
    Sends a login success message to the Discord webhook.
    
    Args:
    - data (list): A list containing Rewards, Login, and Bonus or a string indicating no bonus.
    """
    endpoint = main.webhook_discord_url

    rewards: user.Rewards = data[0]
    login: user.Login = data[1]
    bonus: Union[user.Bonus, str] = data[2]

    try:
        with open('login.json', 'r', encoding='utf-8') as f:
            data22 = json.load(f)
    except FileNotFoundError:
        print("Error: 'login.json' file not found.")
        return
    except json.JSONDecodeError:
        print("Error: 'login.json' contains invalid JSON.")
        return

    name1 = data22['cache']['replaced']['userGame'][0]['name']
    fpids1 = data22['cache']['replaced']['userGame'][0]['friendCode']

    message_bonus = ''
    nl = '\n'

    if isinstance(bonus, user.Bonus):
        message_bonus += f"__{bonus.message}__{nl}```{nl.join(bonus.items)}```"

        if bonus.bonus_name is not None:
            message_bonus += f"{nl}__{bonus.bonus_name}__{nl}{bonus.bonus_detail}{nl}```{nl.join(bonus.bonus_camp_items)}```"

        message_bonus += "\n"
    elif isinstance(bonus, str) and bonus != "No Bonus":
        message_bonus += f"{bonus}\n"

    json_data = {
        "content": None,
        "embeds": [
            {
                "title": f"Fate/Grand Order Daily Login Manager - {main.fate_region}",
                "description": f"Login success.\n\n{message_bonus}",
                "color": dracula_colors["purple"],  # Dracula purple color
                "fields": [
                    {"name": "Master", "value": name1, "inline": True},
                    {"name": "ID", "value": fpids1, "inline": True},
                    {"name": "Master Level", "value": str(rewards.level), "inline": True},
                    {"name": "Summon Ticket", "value": str(rewards.ticket), "inline": True},
                    {"name": "Saint Quartz", "value": str(rewards.stone), "inline": True},
                    {"name": "Saint Quartz Fragment", "value": str(rewards.sqf01), "inline": True},
                    {"name": "Fruits", "value": f"Golden x{rewards.goldenfruit} / x{rewards.silverfruit} Silver / x{rewards.bronzefruit} Bronze/ x{rewards.bluebronzefruit} Blue", "inline": True},
                    {"name": "Bronze Sapling", "value": str(rewards.bluebronzesapling), "inline": True},
                    {"name": "Login Streak", "value": f"{login.login_days} days", "inline": True},
                    {"name": "Total Login Days", "value": f"{login.total_days} days", "inline": True},
                    {"name": "Pure Prism", "value": str(rewards.pureprism), "inline": True},
                    {"name": "FP", "value": str(login.total_fp), "inline": True},
                    {"name": "Gained FP", "value": f"+{login.add_fp}", "inline": True},
                    {"name": "Current AP", "value": str(login.remaining_ap), "inline": True},  # Uncomment if needed
                    {"name": "Holy Grail", "value": str(rewards.holygrail), "inline": True},
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo3/images/commnet_chara16.png"
                }
            }
        ],
        "attachments": []
    }

    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(endpoint, json=json_data, headers=headers)
        print("topLogin response:", response.status_code, response.text)
    except requests.RequestException as e:
        print(f"Error: {e}")

def shop(item: str, total_ap_spent: str, total_items: str) -> None:
    """
    Sends a shop exchange message to the Discord webhook.
    
    Args:
    - item (str): The item purchased.
    - total_ap_spent (str): Total AP points spent.
    - total_items (str): Total items received.
    """
    endpoint = main.webhook_discord_url

    json_data = {
        "content": None,
        "embeds": [
            {
                "title": f"Da Vinci's {item} Shop - {main.fate_region}",
                "description": f"Received {total_items} {item}.",
                "color": dracula_colors["cyan"],  # Dracula cyan color
                "fields": [
                    {"name": "Received", "value": f"Used {total_ap_spent} AP points to get x{total_items} {item} (40 AP each)", "inline": False}
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo3/images/commnet_chara10.png"
                }
            }
        ],
        "attachments": []
    }

    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(endpoint, json=json_data, headers=headers)
        print("shop response:", response.status_code, response.text)
    except requests.RequestException as e:
        print(f"Error: {e}")

def draw_fp(servants: List[object], missions: List[object]) -> None:
    """
    Sends the FP summon results to the Discord webhook.
    
    Args:
    - servants (list): A list of servant objects obtained.
    - missions (list): A list of mission objects completed.
    """
    endpoint = main.webhook_discord_url

    message_mission = ""
    message_servant = ""
    
    if servants:
        try:
            servants_atlas = requests.get("https://api.atlasacademy.io/export/NA/basic_svt.json").json()
        except requests.RequestException as e:
            print(f"Error fetching servants data: {e}")
            return

        svt_dict = {svt["id"]: svt for svt in servants_atlas}

        for servant in servants:
            svt = svt_dict.get(servant.objectId, None)
            if svt:
                message_servant += f"`{svt['name']}` "

    if missions:
        for mission in missions:
            message_mission += f"__{mission.message}__\n{mission.progressTo}/{mission.condition}\n"

    json_data = {
        "content": None,
        "embeds": [
            {
                "title": f"Fate/Grand Order Automatic Summoning - {main.fate_region}",
                "description": f"FP Gacha results.\n\n{message_mission}",
                "color": dracula_colors["green"],  # Dracula green color
                "fields": [
                    {"name": "Received", "value": message_servant, "inline": False}
                ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo3/images/commnet_chara04.png"
                }
            }
        ],
        "attachments": []
    }

    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(endpoint, json=json_data, headers=headers)
        print("drawFP response:", response.status_code, response.text)
    except requests.RequestException as e:
        print(f"Error: {e}")
