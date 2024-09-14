import os
import requests
import time
import json
import fgourl
import user
import coloredlogs
import logging

# Environment variables
userIds = os.environ["userIds"].split(",")
authKeys = os.environ["authKeys"].split(",")
secretKeys = os.environ["secretKeys"].split(",")
webhook_discord_url = os.environ["webhookDiscord"]
device_info = os.environ.get("DEVICE_INFO_SECRET")
user_agent_2 = os.environ.get("USER_AGENT_SECRET_2")
fate_region = "NA"

# Initialize logger
logger = logging.getLogger("FGO Daily Login")
coloredlogs.install(fmt="%(asctime)s %(name)s %(levelname)s %(message)s")


def get_latest_verCode():
    """Fetch the latest version code from the VerCode API."""
    endpoint = f"https://raw.githubusercontent.com/xdeadboy666x/FGO-JP-NA-VerCode-Extractor/{fate_region}/VerCode.json"
    response = requests.get(endpoint).text
    response_data = json.loads(response)
    return response_data["verCode"]


def get_latest_appver():
    """Fetch the latest app version from the VerCode API."""
    endpoint = f"https://raw.githubusercontent.com/xdeadboy666x/FGO-JP-NA-VerCode-Extractor/{fate_region}/VerCode.json"
    response = requests.get(endpoint).text
    response_data = json.loads(response)
    return response_data["appVer"]


def main():
    if len(userIds) == len(authKeys) == len(secretKeys):
        fgourl.set_latest_assets()
        for i in range(len(userIds)):
            try:
                # Create user instance and perform operations
                instance = user.user(userIds[i], authKeys[i], secretKeys[i])
                logger.info(
                    f"\n ======================================== \n [+] Logging in account: {userIds[i]} \n ======================================== "
                )

                # Call instance methods with delays
                time.sleep(3)
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
                instance.drawFP()

            except requests.exceptions.RequestException as ex:
                logger.error(f"Network error: {ex}")
            except Exception as ex:
                logger.error(f"An error occurred: {ex}")
    else:
        logger.error("Mismatch in the number of userIds, authKeys, and secretKeys")


if __name__ == "__main__":
    main()
