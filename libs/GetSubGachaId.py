from typing import List
import requests
from mytime import GetTimeStamp

def isMatchedQuestCondition(region: str, userQuest: List, commonReleaseId: int):
    api = f"https://api.atlasacademy.io/nice/{region}/common-release/{commonReleaseId}"
    response = requests.get(api)
    response.raise_for_status()
    condition = response.json()
    if condition and condition[0].get("condType", "") == "questClear":
        condQuestId = condition[0]["condId"]
        condClearNum = condition[0]["condNum"]
        for quest in userQuest:
            if quest["questId"] == condQuestId and quest["clearNum"] > condClearNum:
                return True
            elif quest["questId"] == condQuestId and quest["clearNum"] <= condClearNum:
                return False
        return False
    else:
        # Placeholder for webhook error handling
        pass

def GetGachaSubIdFP(region, userQuest: List = []):
    api = f"https://git.atlasacademy.io/atlasacademy/fgo-game-data/raw/branch/NA/master/mstGachaSub.json"
    response = requests.get(api)
    data = list(response.json())
    data.reverse()

    timeNow = GetTimeStamp()
    activeGacha = []
    for gacha in data:
        if gacha["closedAt"] > timeNow and gacha["openedAt"] < timeNow:
            activeGacha.append(gacha)
        else:
            break

    if not activeGacha:
        # Placeholder for webhook error handling
        pass

    sortedGachaList = sorted(activeGacha, key=lambda x: (x["priority"], x["commonReleaseId"]), reverse=True)
    for gacha in sortedGachaList:
        if gacha["commonReleaseId"] != 0 and isMatchedQuestCondition(region, userQuest, gacha["commonReleaseId"]):
            return gacha["id"]
        elif gacha["commonReleaseId"] == 0:
            return gacha["id"]
