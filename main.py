import os
import requests
import time
import json
from datetime import datetime
from croniter import croniter
import fgourl
import user
import coloredlogs
import logging

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
    logging.error(f"Missing environment variable: {e}")
    raise

if UA:
    fgourl.user_agent_ = UA

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
            instance.buyBlueApple(1)
            time.sleep(2)


def get_latest_verCode():
    endpoint = "https://raw.githubusercontent.com/xdeadboy666x/FGO-JP-NA-VerCode-Extractor/NA/VerCode.json"
    try:
        response = requests.get(endpoint)
        if response.status_code == 200:
            response_data = response.json()
            return response_data['verCode']
        else:
            logger.error(f"Unexpected response code: {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error fetching latest verCode: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON response: {e}")
        return None


def main():
    if userNums == authKeyNums and userNums == secretKeyNums:
        logger.info('Fetching Game Data')
        fgourl.set_latest_assets()

        for i in range(userNums):
            try:
                instance = user.user(userIds[i], authKeys[i], secretKeys[i])
                time.sleep(3)
                logger.info('Logging in...')
                response = instance.topLogin()
                logger.debug(f"topLogin response: {response.status_code} - {response.text}")
                if response.status_code == 204:
                    logger.info('No content returned from topLogin')
                else:
                    time.sleep(2)
                    instance.topHome()
                    time.sleep(2)
                    instance.lq001()
                    instance.lq002()
                    time.sleep(2)

                    check_blue_apple_cron(instance)

                    logger.info('Summoning with FP!')
                    try:
                        instance.FPsummon()
                        time.sleep(4)
                    except Exception as ex:
                        logger.error(f"FP summoning failed: {ex}")

                    logger.info('Exchanging Blue Fruit!')
                    try:
                        for _ in range(4):
                            instance.buyBlueApple(1)
                            time.sleep(2)
                    except Exception as ex:
                        logger.error(ex)

            except Exception as ex:
                logger.error(ex)


if __name__ == "__main__":
    main()
