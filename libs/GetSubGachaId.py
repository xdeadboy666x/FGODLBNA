import requests
import json
from mytime import GetTimeStamp

def get_gacha_sub_id_fp(region):
    """
    Fetches the Friend Summon Gacha Sub ID for a given region if it is currently open.
    
    Args:
    - region (str): The region code for the gacha data.
    
    Returns:
    - str: The ID of the currently open gacha or None if no gacha is open.
    """
    url = f"https://git.atlasacademy.io/atlasacademy/fgo-game-data/raw/branch/{region}/master/mstGachaSub.json"
    response = requests.get(url)
    response.raise_for_status()  # Ensure we raise an error for bad responses
    gacha_list = response.json()  # Directly parse JSON response
    time_now = GetTimeStamp()

    for gacha in gacha_list:
        opened_at = gacha["openedAt"]
        closed_at = gacha["closedAt"]

        if opened_at <= time_now <= closed_at:
            return str(gacha["id"])

    return None  # Explicitly return None if no gacha is open

# Alias for backward compatibility
GetGachaSubIdFP = get_gacha_sub_id_fp