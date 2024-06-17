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
userIds = os.environ['userIds'].split(',')
authKeys = os.environ['authKeys'].split(',')
secretKeys = os.environ['secretKeys'].split(',')
fate_region = os.environ['fateRegion']
webhook_discord_url = os.environ['webhookDiscord']
blue_apple_cron = os.environ.get("MAKE_BLUE_APPLE")
UA = os.environ['UserAgent']

if UA:
    fgourl.user_agent_ = UA

userNums = len(userIds)
authKeyNums = len(authKeys)
secretKeyNums = len(secretKeys)

# Logger setup
logger = logging.getLogger("FGO Daily Login")
coloredlogs.install(fmt='%(asctime)s %(name)s %(levelname)s %(message)s', logger=logger)

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
    endpoint = "https://raw.githubusercontent.com/xdeadboy666x/FGO-VerCode-extractor/NA/VerCode.json"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        response_data = response.json()
        return response_data['verCode']
    except requests.RequestException as e:
        logger.error(f"Failed to fetch the latest version code: {e}")
        raise

def GetGachaSubIdFP(region):
    try:
        response = requests.get(f"https://git.atlasacademy.io/atlasacademy/fgo-game-data/raw/branch/{region}/master/mstGachaSub.json")
        response.raise_for_status()
        gachaList = response.json()
        timeNow = int(time.time())
        priority = 0
        goodGacha = {}
        for gacha in gachaList:
            openedAt = gacha["openedAt"]
            closedAt = gacha["closedAt"]

            if openedAt <= timeNow <= closedAt:
                p = int(gacha["priority"])
                if p > priority:
                    priority = p
                    goodGacha = gacha
        return str(goodGacha.get("id", None))  # Return None if no valid Gacha ID is found
    except requests.RequestException as e:
        logger.error(f"Failed to fetch Gacha Sub ID: {e}")
        return None

def main():
    if userNums == authKeyNums == secretKeyNums:
        logger.info('Fetching Game Data')
        try:
            fgourl.set_latest_assets()
        except Exception as ex:
            logger.error(f"Failed to set latest assets: {ex}")
            return

        gachaSubId = GetGachaSubIdFP(fate_region)
        logger.info(f"Friend Point Gacha Sub Id: {gachaSubId}")

        for i in range(userNums):
            try:
                instance = user.user(userIds[i], authKeys[i], secretKeys[i])
                time.sleep(3)
                logger.info(f'Logging in to account {i+1}/{userNums}')

                try:
                    instance.topLogin()
                except AttributeError:
                    instance.topLogin2()
                time.sleep(2)
                instance.topHome()
                time.sleep(2)

                instance.lq001()
                instance.lq002()
                time.sleep(2)

                check_blue_apple_cron(instance)

                logger.info('Exchanging Blue Fruit!')
                try:
                    instance.buyBlueApple(1)
                    time.sleep(2)
                    for _ in range(3):
                        instance.buyBlueApple(1)
                        time.sleep(2)
                except Exception as ex:
                    logger.error(ex)

                try:
                    logger.info('Pulling FP Summon!')
                    for _ in range(1):
                        instance.drawFP()
                        time.sleep(4)
                except Exception as ex:
                    logger.error(f"Failed during FP summon: {ex}, Current Gacha Sub ID: {gachaSubId}")

            except Exception as ex:
                logger.error(f"Error during user operation: {ex}")
    else:
        logger.error("Mismatch in the number of userIds, authKeys, and secretKeys")

if __name__ == "__main__":
    main()
