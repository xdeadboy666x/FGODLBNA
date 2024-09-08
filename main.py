import os
import requests
import time
import json
import fgourl
import user
import coloredlogs
import logging

# Enviroments Variables
userIds = os.environ['userIds'].split(',')
authKeys = os.environ['authKeys'].split(',')
secretKeys = os.environ['secretKeys'].split(',')
fate_region = os.environ['fateRegion']
webhook_discord_url = os.environ['webhookDiscord']
blue_apple_cron = os.environ.get("MAKE_BLUE_APPLE")
idempotency_key_signature = os.environ.get('IDEMPOTENCY_KEY_SIGNATURE_SECRET')


UA = os.environ['UserAgent']

if UA:
    fgourl.user_agent_ = UA

userNums = len(userIds)
authKeyNums = len(authKeys)
secretKeyNums = len(secretKeys)

logger = logging.getLogger("FGO Daily Login")
coloredlogs.install(fmt='%(asctime)s %(name)s %(levelname)s %(message)s')

def get_latest_verCode():
    endpoint = ""

    if fate_region == "NA":
        endpoint += "https://raw.githubusercontent.com/xdeadboy666x/FGO-JP-NA-VerCode-Extractor/NA/VerCode.json"
    else:
        endpoint += "https://raw.githubusercontent.com/xdeadboy666x/FGO-JP-NA-VerCode-Extractor/JP/VerCode.json"

    response = requests.get(endpoint).text
    response_data = json.loads(response)

    return response_data['verCode']
    
def get_latest_appver():
    endpoint = "https://raw.githubusercontent.com/xdeadboy666x/FGO-JP-NA-VerCode-Extractor/NA/VerCode.json"
    response = requests.get(endpoint).text
    response_data = json.loads(response)

    return response_data['appVer']

def main():
    if userNums == authKeyNums and userNums == secretKeyNums:
        logger.info('Getting Lastest Assets Info')
        fgourl.set_latest_assets()

        for i in range(userNums):
            try:
                instance = user.user(userIds[i], authKeys[i], secretKeys[i])
                time.sleep(3)
                logger.info('Signing in!')
                instance.topLogin()
                time.sleep(2)
                instance.topHome()
                time.sleep(2)
                instance.buyBlueApple()
                instance.lq001()
                instance.lq002()
                time.sleep(1)
                instance.lq003()
                time.sleep(1)
                instance.zc15()
                
                #instance.zc16()
                #instance.zc25() #导出账号功能
                
                time.sleep(1)
                instance.drawFP()
                #for _ in range(100): 
                      #instance.drawS()
                      #instance.drawFF()
                      #time.sleep(1)
                    
            except Exception as ex:
                logger.error(ex)


if __name__ == "__main__":
    main()
