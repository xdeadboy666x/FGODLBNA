import os
import requests
import time
import logging
from datetime import datetime
from croniter import croniter
import fgourl
import user
import coloredlogs

# Setup logger
logger = logging.getLogger("FGO Daily Login")
coloredlogs.install(fmt='%(asctime)s %(name)s %(levelname)s %(message)s')

def get_env_var(var_name):
    """
    Retrieve environment variable and split it into a list by commas.
    Raise an error if the variable is not set.
    """
    value = os.environ.get(var_name)
    if not value:
        logger.error(f"Environment variable {var_name} is not set.")
        raise EnvironmentError(f"Environment variable {var_name} is not set.")
    return value.split(',')

try:
    userIds = get_env_var('userIds')
    authKeys = get_env_var('authKeys')
    secretKeys = get_env_var('secretKeys')
    webhook_discord_url = os.environ.get('webhookDiscord')
    device_info = os.environ.get('DEVICE_INFO_SECRET')
    user_agent_2 = os.environ.get('USER_AGENT_SECRET_2')
except EnvironmentError as e:
    logger.critical(e)
    exit(1)

userNums = len(userIds)
authKeyNums = len(authKeys)
secretKeyNums = len(secretKeys)

def get_latest_verCode():
    """
    Fetch the latest version code from a predefined endpoint.
    """
    try:
        endpoint = "https://raw.githubusercontent.com/xdeadboy666x/FGO-JP-NA-VerCode-Extractor/JP/VerCode.json"
        response = requests.get(endpoint)
        response.raise_for_status()
        response_data = response.json()
        return response_data['verCode']
    except requests.RequestException as e:
        logger.error(f"Failed to get the latest verCode: {e}")
        raise

def main():
    """
    Main function to login to multiple user accounts and perform daily tasks.
    """
    if userNums == authKeyNums == secretKeyNums:
        try:
            fgourl.set_latest_assets()
        except Exception as ex:
            logger.error(f"Failed to set latest assets: {ex}")
            return

        for i in range(userNums):
            try:
                instance = user.user(userIds[i], authKeys[i], secretKeys[i])
                logger.info(f"Logging in to account {i+1}/{userNums}")

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
            except Exception as ex:
                logger.error(f"Error with account {i+1}/{userNums}: {ex}")
    else:
        logger.error("The number of user IDs, auth keys, and secret keys do not match.")
        raise ValueError("Mismatched user IDs, auth keys, and secret keys count.")

if __name__ == "__main__":
    main()
