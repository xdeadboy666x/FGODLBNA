import json
import binascii
import requests
import main
import CatAndMouseGame
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FGO Daily Login")

requests.urllib3.disable_warnings()
session = requests.Session()
session.verify = False

# ===== Game's parameters =====
app_ver_ = ''
data_ver_ = 0
date_ver_ = 0
ver_code_ = ''
asset_bundle_folder_ = ''
data_server_folder_crc_ = 0
server_addr_ = 'https://game.fate-go.us'
github_token_ = ''
github_name_ = ''

# ==== User Info ====
def set_latest_assets():
    global app_ver_, data_ver_, date_ver_, asset_bundle_folder_, data_server_folder_crc_, ver_code_, server_addr_

    region = main.fate_region

    # Set Game Server Depends of region
    if region == "NA":
        server_addr_ = "https://game.fate-go.us"

    # Get Latest Version of the data!
    version_str = main.get_latest_appver()
    logger.info(f"version_str: {version_str}")
    if not version_str:
        raise ValueError("Failed to get latest app version")

    response = requests.get(
        server_addr_ + '/gamedata/top?appVer=' + version_str).text
    logger.debug(f"Response from server: {response}")

    try:
        response_data = json.loads(response)["response"][0]["success"]
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logger.error(f"Error parsing JSON response: {e}")
        raise

    # Set AppVer, DataVer, DateVer
    app_ver_ = version_str
    data_ver_ = response_data.get('dataVer')
    date_ver_ = response_data.get('dateVer')
    ver_code_ = main.get_latest_verCode()

    logger.info(f"data_ver_: {data_ver_}, date_ver_: {date_ver_}, ver_code_: {ver_code_}")

    if 'assetbundle' not in response_data:
        raise ValueError("Missing 'assetbundle' in response data")

    # Use Asset Bundle Extractor to get Folder Name
    assetbundle = CatAndMouseGame.getAssetBundle(response_data['assetbundle'])
    get_folder_data(assetbundle)


def get_folder_data(assetbundle):
    global asset_bundle_folder_, data_server_folder_crc_

    if 'folderName' not in assetbundle:
        raise ValueError("Missing 'folderName' in assetbundle")

    asset_bundle_folder_ = assetbundle['folderName']
    logger.info(f"asset_bundle_folder_: {asset_bundle_folder_}")

    data_server_folder_crc_ = binascii.crc32(
        asset_bundle_folder_.encode('utf8'))
    logger.info(f"data_server_folder_crc_: {data_server_folder_crc_}")

# ===== End =====

user_agent_2 = os.environ.get('USER_AGENT_SECRET_2')

httpheader = {
    'User-Agent': user_agent_2,
    "Accept-Encoding": "gzip, identity",
    "Content-Type": "application/x-www-form-urlencoded"
}

def NewSession():
    return requests.Session()

def PostReq(s, url, data):
    res = s.post(url, data=data, headers=httpheader, verify=False).json()
    res_code = res['response'][0]['resCode']

    if res_code != '00':
        detail = res['response'][0]['fail']['detail']
        message = f'[ErrorCode: {res_code}]\n{detail}'
        raise Exception(message)

    return res