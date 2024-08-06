import os
import requests
import time
import json
import fgourl
import user
import coloredlogs
import logging

# Environment variables
userIds = os.environ['userIds'].split(',')
authKeys = os.environ['authKeys'].split(',')
secretKeys = os.environ['secretKeys'].split(',')
webhook_discord_url = os.environ['webhookDiscord']
device_info = os.environ.get('DEVICE_INFO_SECRET')
user_agent_2 = os.environ.get('USER_AGENT_SECRET_2')
fate_region = 'NA'

# Counts of users, auth keys, and secret keys
userNums = len(userIds)
authKeyNums = len(authKeys)
secretKeyNums = len(secretKeys)

# Logger setup
logger = logging.getLogger("Fate/Grand Order Login Manager")
coloredlogs.install(fmt='%(asctime)s %(name)s %(levelname)s %(message)s')

def get_latest_verCode():
    endpoint = f'https://raw.githubusercontent.com/xdeadboy666x/FGO-JP-NA-VerCode-Extractor/{fate_region}/VerCode.json'
    response = requests.get(endpoint).text
    response_data = json.loads(response)
    return response_data['verCode']
    
def get_latest_appver():
    endpoint = f'https://raw.githubusercontent.com/xdeadboy666x/FGO-JP-NA-VerCode-Extractor/{fate_region}/VerCode.json'
    response = requests.get(endpoint).text
    response_data = json.loads(response)
    return response_data['appVer']

def main():
    if userNums == authKeyNums and userNums == secretKeyNums:
        fgourl.set_latest_assets()
        for i in range(userNums):
            try:
                instance = user.User(userIds[i], authKeys[i], secretKeys[i])
                time.sleep(3)
                logger.info("\n ======================================== \n [+] Signing in \n ======================================== ")

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
                logger.error(ex)

if __name__ == "__main__":
    main()