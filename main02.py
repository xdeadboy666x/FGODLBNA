import os
import requests
import time
import json
import fgourl
import user
import coloredlogs
import logging
from datetime import datetime
from croniter import croniter

# Environment Variables
try:
    userIds = os.environ['userIds'].split(',')
    authKeys = os.environ['authKeys'].split(',')
    secretKeys = os.environ['secretKeys'].split(',')
    fate_region = os.environ['fateRegion']
    webhook_discord_url = os.environ['webhookDiscord']
    blue_apple_cron = os.environ.get("MAKE_BLUE_APPLE")
    UA = os.environ['UserAgent']
except KeyError as e:
    raise EnvironmentError(f"Missing environment variable: {e}")

if UA:
    try:
        fgourl.user_agent_ = UA
    except AttributeError:
        raise AttributeError("`fgourl` module does not have `user_agent_` attribute.")

userNums = len(userIds)
authKeyNums = len(authKeys)
secretKeyNums = len(secretKeys)

logger = logging.getLogger("FGO Daily Login")
coloredlogs.install(fmt='%(asctime)s %(name)s %(levelname)s %(message)s')

def check_blue_apple_cron(instance):
    if blue_apple_cron:
        cron = croniter(blue_apple_cron)
        next_date = cron.get_next(datetime)
        current_date = datetime.now()
        if current_date >= next_date:
            logger.info('Exchanging Blue Fruit!')
            try:
                instance.buyBlueApple(1)
            except Exception as ex:
                logger.error(f"Error buying Blue Apple: {ex}")
            time.sleep(2)

def get_latest_verCode():
    endpoint = "https://raw.githubusercontent.com/xdeadboy666x/FGO-VerCode-extractor/NA/VerCode.json"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        response_data = response.json()
        return response_data['verCode']
    except requests.RequestException as e:
        logger.error(f"Error fetching latest verCode: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding verCode JSON: {e}")
        return None

def main():
    if userNums == authKeyNums == secretKeyNums:
        logger.info('Fetching Game Data')
        try:
            fgourl.set_latest_assets()
        except Exception as ex:
            logger.error(f"Error setting latest assets: {ex}")
            return

        for i in range(userNums):
            try:
                instance = user.user(userIds[i], authKeys[i], secretKeys[i])
                time.sleep(3)
                logger.info('Login in...')
                instance.topLogin2()
                time.sleep(2)
                instance.topHome()
                time.sleep(2)
                try:
                    logger.info('Pulling FP Summon!')
                    for _ in range(1):
                        instance.drawFP()
                        time.sleep(4)
                except Exception as ex:
                    logger.error(f"Error during FP Summon: {ex}")
            except Exception as ex:
                logger.error(f"Error with user instance {i}: {ex}")
    else:
        logger.error('Mismatch in userIds, authKeys, and secretKeys lengths.')

if __name__ == "__main__":
    main()
