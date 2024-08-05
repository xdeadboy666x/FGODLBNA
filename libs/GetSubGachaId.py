import requests
import json
from mytime import GetTimeStamp

# Get Friend Summon Gacha Sub Id
def GetGachaSubIdFP(region):
    response = requests.get(f"https://git.atlasacademy.io/atlasacademy/fgo-game-data/raw/branch/{region}/master/mstGachaSub.json")
    gachaList = json.loads(response.text)
    timeNow = GetTimeStamp()
    priority = 0
    goodGacha = {}
    
    for gacha in gachaList:
        openedAt = gacha["openedAt"]
        closedAt = gacha["closedAt"]

        if openedAt <= timeNow and timeNow <= closedAt:  # Fixed the logical operator
            p = int(gacha["priority"])
            if p > priority:
                priority = p
                goodGacha = gacha
                
    if goodGacha:
        return str(goodGacha["id"])
    else:
        return None  # Return None if no valid Gacha ID is found

# Example usage
region = "NA"
gachaSubId = GetGachaSubIdFP(region)
print(f"Current Gacha Sub ID: {gachaSubId}")