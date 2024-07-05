import json
import binascii
import requests
import os
import version
import main
import CatAndMouseGame

# Disable insecure request warnings
requests.urllib3.disable_warnings()

# Function to retrieve user agent from environment variables
def get_user_agent():
    return os.environ.get('USER_AGENT_SECRET')

# Global variables (consider avoiding global variables if possible)
session = requests.Session()
session.verify = False
server_addr_ = 'https://game.fate-go.jp'
github_token_ = ''  # Unused in provided snippet
github_name_ = ''  # Unused in provided snippet

# Game's parameters
app_ver_ = ''
data_ver_ = 0
date_ver_ = 0
ver_code_ = ''
asset_bundle_folder_ = ''
data_server_folder_crc_ = 0
user_agent_ = get_user_agent()

# HTTP headers
httpheader = {
    'Accept-Encoding': 'gzip, identity',
    'User-Agent': user_agent_ if user_agent_ else '',  # Handle potential None value
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'Keep-Alive, TE',
    'TE': 'identity',
    'X-Unity-Version': "2022.3.28f1"
}

def set_latest_assets():
    global app_ver_, data_ver_, date_ver_, asset_bundle_folder_, data_server_folder_crc_, server_addr_

    region = main.fate_region  # Assuming fate_region is defined in main module

    if region == "NA":
        server_addr_ = "https://game.fate-go.us"

    # Get Latest Version of the data
    version_str = version.get_version(region)  # Ensure version module has this function
    response = requests.get(f'{server_addr_}/gamedata/top?appVer={version_str}').text
    response_data = json.loads(response)["response"][0]["success"]

    # Set AppVer, DataVer, DateVer
    app_ver_ = version_str
    data_ver_ = response_data['dataVer']
    date_ver_ = response_data['dateVer']

    # Get assetbundle and extract folder name
    assetbundle = CatAndMouseGame.getAssetBundle(response_data['assetbundle'])
    get_folder_data(assetbundle)

def get_folder_data(assetbundle):
    global asset_bundle_folder_, data_server_folder_crc_

    asset_bundle_folder_ = assetbundle['folderName']
    data_server_folder_crc_ = binascii.crc32(assetbundle['folderName'].encode('utf8'))

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
