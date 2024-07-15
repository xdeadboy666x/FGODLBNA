import os
import requests
import time
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

# Logger setup
logger = logging.getLogger("FGO Daily Login")
coloredlogs.install(fmt='%(asctime)s %(name)s %(levelname)s %(message)s', logger=logger)

def check_blue_apple_cron(instance):
    """Check if the blue apple cron schedule has reached and perform the exchange if necessary."""
    if blue_apple_cron:
        cron = croniter(blue_apple_cron)
        next_date = cron.get_next(datetime)
        current_date = datetime.now()
        
        if current_date >= next_date:
            logger.info('Exchanging Blue Fruit!')
            instance.buyBlueApple(1)
            time.sleep(2)

def get_latest_verCode():
    """Fetch the latest version code from the given endpoint."""
    endpoint = "https://raw.githubusercontent.com/xdeadboy666x/FGO-JP-NA-VerCode-Extractor/NA/VerCode.json"
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        response_data = response.json()
        return response_data['verCode']
    except requests.RequestException as e:
        logger.error(f"Failed to fetch the latest version code: {e}")
        raise

def main():
    """Main function to handle the daily login process for FGO."""
    if len(userIds) == len(authKeys) == len(secretKeys):
        logger.info('Fetching Game Data')
        try:
            fgourl.set_latest_assets()
        except Exception as ex:
            logger.error(f"Failed to set latest assets: {ex}")
            return

        for i in range(len(userIds)):
            try:
                instance = user.user(userIds[i], authKeys[i], secretKeys[i])
                time.sleep(3)
                
                logger.info('Logging in...')
                instance.topLogin()
                time.sleep(2)
                instance.topHome()
                time.sleep(2)
                instance.lq001()
                instance.lq002()
                time.sleep(2)
                
                check_blue_apple_cron(instance)
                
                logger.info('Pulling FP Summon!')
                try:
                    instance.drawFP()
                    time.sleep(4)
                except Exception as ex:
                    logger.error(f"Failed during FP summon: {ex}")

                logger.info('Exchanging Blue Fruit!')
                try:
                    for _ in range(4):  # Exchanging once in check_blue_apple_cron and three times here
                        instance.buyBlueApple(1)
                        time.sleep(2)
                except Exception as ex:
                    logger.error(f"Failed during blue apple exchange: {ex}")
                
            except Exception as ex:
                logger.error(f"Error during user operation for user {userIds[i]}: {ex}")
    else:
        logger.error("Mismatch in the number of userIds, authKeys, and secretKeys")

if __name__ == "__main__":
    main()
