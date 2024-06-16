import json
import binascii
import requests
import os
import version
import main
import CatAndMouseGame

requests.urllib3.disable_warnings()
session = requests.Session()
session.verify = False

# ===== Constants =====
NA_SERVER_ADDR = "https://game.fate-go.us"
JP_SERVER_ADDR = "https://game.fate-go.jp"
UNITY_VERSION = "2020.3.34f1"
CONTENT_TYPE = "application/x-www-form-urlencoded"

# ===== Global Variables =====
app_ver_ = ''
data_ver_ = 0
date_ver_ = 0
ver_code_ = ''
asset_bundle_folder_ = ''
data_server_folder_crc_ = 0
server_addr_ = JP_SERVER_ADDR
github_token_ = ''
github_name_ = ''

# ==== User Info ====
def set_latest_assets():
    global app_ver_, data_ver_, date_ver_, asset_bundle_folder_, data_server_folder_crc_, ver_code_, server_addr_

    region = main.fate_region

    # Set Game Server Depends on the region
    if region == "NA":
        server_addr_ = NA_SERVER_ADDR

    # Get Latest Version of the data
    version_str = version.get_version(region)
    try:
        response = requests.get(f'{server_addr_}/gamedata/top?appVer={version_str}').text
        response_data = json.loads(response)["response"][0]["success"]

        # Set AppVer, DataVer, DateVer
        app_ver_ = version_str
        data_ver_ = response_data['dataVer']
        date_ver_ = response_data['dateVer']
        ver_code_ = main.get_latest_verCode()

        # Use Asset Bundle Extractor to get Folder Name
        assetbundle = CatAndMouseGame.getAssetBundle(response_data['assetbundle'])
        get_folder_data(assetbundle)
    except requests.RequestException as e:
        raise Exception(f"Network error: {e}")
    except (KeyError, json.JSONDecodeError) as e:
        raise Exception(f"Data parsing error: {e}")

def get_folder_data(assetbundle):
    global asset_bundle_folder_, data_server_folder_crc_

    asset_bundle_folder_ = assetbundle['folderName']
    data_server_folder_crc_ = binascii.crc32(assetbundle['folderName'].encode('utf8'))

# ===== End =====

user_agent_ = os.environ.get('USER_AGENT_SECRET')
if not user_agent_:
    raise EnvironmentError("USER_AGENT_SECRET environment variable is not set")

httpheader = {
    'User-Agent': user_agent_,
    'Accept-Encoding': "deflate, gzip",
    'Content-Type': CONTENT_TYPE,
    'X-Unity-Version': UNITY_VERSION
}

def NewSession():
    return requests.Session()

def PostReq(s, url, data):
    try:
        res = s.post(url, data=data, headers=httpheader, verify=False).json()
        res_code = res['response'][0]['resCode']

        if res_code != '00':
            detail = res['response'][0]['fail']['detail']
            message = f'[ErrorCode: {res_code}]\n{detail}'
            raise Exception(message)

        return res
    except requests.RequestException as e:
        raise Exception(f"Network error: {e}")
    except KeyError as e:
        raise Exception(f"Data parsing error: {e}")
