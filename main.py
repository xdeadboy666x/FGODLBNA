import os
import requests
import time
import json
import fgourl
import user
import coloredlogs
import logging
from pathlib import Path
from typing import Any
import orjson

# Environment variables
userIds = os.environ['userIds'].split(',')
authKeys = os.environ['authKeys'].split(',')
secretKeys = os.environ['secretKeys'].split(',')
webhook_discord_url = os.environ['webhookDiscord']
device_info = os.environ.get('DEVICE_INFO_SECRET')
user_agent_2 = os.environ.get('USER_AGENT_SECRET_2')
fate_region = 'NA'

userNums = len(userIds)
authKeyNums = len(authKeys)
secretKeyNums = len(secretKeys)

# Set up logging
logger = logging.getLogger("FGO Daily Login")
coloredlogs.install(fmt='%(asctime)s %(name)s %(levelname)s %(message)s')

# Function to load JSON from file
def load_json(fp: str | Path, _default=None) -> Any:
    fp = Path(fp)
    if fp.exists():
        return orjson.loads(fp.read_bytes())
    return _default

# Function to dump JSON to file
def dump_json(obj, fp: str | Path | None = None, indent=False, default=None) -> str:
    option = orjson.OPT_NON_STR_KEYS
    if indent:
        option |= orjson.OPT_INDENT_2 | orjson.OPT_APPEND_NEWLINE
    result = orjson.dumps(obj, option=option, default=default)
    if fp:
        fp = Path(fp).resolve()
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_bytes(result)
    return result.decode()

# Function to send a message to Discord webhook
def send_discord_msg(msg: str):
    if not webhook_discord_url:
        return
    try:
        logger.info(f"Sending discord webhook: {msg}")
        resp = requests.post(
            webhook_discord_url,
            json={
                "username": "Daily Bonus",
                "content": f"```\n{msg}\n```",
            },
        )
        logger.info(f"Discord webhook response: {resp.status_code}")
    except Exception as e:
        logger.exception("Failed to send discord webhook")

# Function to get the latest version code
def get_latest_verCode():
    endpoint = "https://raw.githubusercontent.com/xdeadboy666x/FGO-JP-NA-VerCode-Extractor/NA/VerCode.json"
    response = requests.get(endpoint).text
    response_data = json.loads(response)

    return response_data['verCode']

# Function to get the latest app version
def get_latest_appver():
    endpoint = "https://raw.githubusercontent.com/xdeadboy666x/FGO-JP-NA-VerCode-Extractor/NA/VerCode.json"
    response = requests.get(endpoint).text
    response_data = json.loads(response)

    return response_data['appVer']

# Main function that logs into FGO accounts and performs tasks
def main():
    if userNums == authKeyNums and userNums == secretKeyNums:
        fgourl.set_latest_assets()
        for i in range(userNums):
            try:
                instance = user.user(userIds[i], authKeys[i], secretKeys[i])
                time.sleep(3)
                logger.info(f"\n ======================================== \n [+] Logging into account \n ======================================== ")

                time.sleep(1)
                instance.topLogin_s()
                time.sleep(2)
                instance.topHome()
                time.sleep(2)
                instance.lq001()
                instance.lq002()
                time.sleep(2)
                instance.buyBlueApple()
                time.sleep(1)
                instance.lq003()
                time.sleep(1)
                instance.drawFP()

                # Send a message to Discord after the login
                send_discord_msg(f"Successfully logged in for user {userIds[i]}")

            except Exception as ex:
                logger.error(ex)
                send_discord_msg(f"Failed to log in for user {userIds[i]}. Error: {ex}")

if __name__ == "__main__":
    main()
