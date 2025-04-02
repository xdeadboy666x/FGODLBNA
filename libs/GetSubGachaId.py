import requests
import json
import main

from mytime import GetTimeStamp

def GetGachaSubIdFP():
    response = requests.get(f"https://git.atlasacademy.io/atlasacademy/fgo-game-data/raw/branch/NA/master/mstGachaSub.json");
    gachaList = json.loads(response.text)
    timeNow = GetTimeStamp()
    priority = 0
    goodGacha = {}

    for gacha in gachaList:
        openedAt = gacha["openedAt"]
        closedAt = gacha["closedAt"]

        # 修正逻辑运算符
        if openedAt <= timeNow and timeNow <= closedAt:
            p = int(gacha["priority"])
            if p > priority:
                priority = p
                goodGacha = gacha

    # 检查是否找到了合适的 gacha
    if not goodGacha:
        main.logger.info("No suitable gacha found")
        return None  

    # 确认 'id' 键是否存在
    if "id" not in goodGacha:
        main.logger.info("Key 'id' not found in the selected gacha")
        return None  

    return str(goodGacha["id"])