import requests
import json
import uuid
import hashlib
import base64
import time
import os
from urllib.parse import quote_plus
import py3rijndael
import gzip
import msgpack
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import binascii
from Crypto.Cipher import DES3
from datetime import datetime, timedelta, timezone
tz_utc_8 = timezone(timedelta(hours=8))

def get_ver_code(REGION):
    url = f"https://fgo.bigcereal.com/{REGION}/verCode.txt"
    response = requests.get(url)
    data = response.text.strip()
    params = dict(item.split('=') for item in data.split('&'))
    appVer = params.get("appVer")
    verCode = params.get("verCode")
    return appVer, verCode

REGION = os.environ.get("FATE_REGION", "JP")
APP_VER = get_ver_code(REGION)[0]
VER_CODE = get_ver_code(REGION)[1]
USER_AGENT = os.environ.get("USER_AGENT_SECRET_2", "Dalvik/2.1.0 (Linux; U; Android 9 Build/PQ3A.190605.09261202)")
DEVICE_INFO = os.environ.get("DEVICE_INFO_SECRET", "  / Android OS 9 / API-28 (PQ3A.190605.09261202 release-keys/3793265)")
SERVER_ADDR = "https://game.fate-go.jp"  if REGION == "JP" else "https://game.fate-go.us"


def GetNowTimeHour():
    return datetime.now(tz=tz_utc_8).hour


def GetNowTime():
    return datetime.now(tz=tz_utc_8)


def GetFormattedNowTime():
    return datetime.now(tz=tz_utc_8).strftime('%Y-%m-%d %H:%M:%S')


def GetTimeStamp():
    return (int)(datetime.now(tz=tz_utc_8).timestamp())


def TimeStampToString(timestamp):
    return datetime.fromtimestamp(timestamp)


def GetNowTimeFileName():
    return datetime.now(tz=tz_utc_8).strftime('%Y/%m/%d.log')

def get_time_stamp():
    return str(int(time.time()))

def get_asset_bundle(assetbundle):
    data = base64.b64decode(assetbundle)
    key = b'nn33CYId2J1ggv0bYDMbYuZ60m4GZt5P'  # NA key
    if REGION == "JP":
        key = b'W0Juh4cFJSYPkebJB9WpswNF51oa6Gm7'  # JP key
    iv = data[:32]
    array = data[32:]
    cipher = py3rijndael.RijndaelCbc(
        key,
        iv,
        py3rijndael.paddings.Pkcs7Padding(16),
        32
    )
    data = cipher.decrypt(array)
    gzip_data = gzip.decompress(data)
    data_unpacked = msgpack.unpackb(gzip_data)

    return data_unpacked

def get_folder_data(assetbundle):
    folder_name = assetbundle['folderName']
    folder_crc = binascii.crc32(folder_name.encode('utf8'))
    return folder_name, folder_crc

def get_latest_game_data():
    response = requests.get(f"{SERVER_ADDR}/gamedata/top?appVer={APP_VER}").json()
    data = response["response"][0]["success"]
    asset_bundle = get_asset_bundle(data['assetbundle'])
    folder_name, folder_crc = get_folder_data(asset_bundle)
    return {
        "data_ver": data['dataVer'],
        "date_ver": data['dateVer'],
        "asset_bundle": {
            "folderName": folder_name,
            "folderCrc": folder_crc
        }
    }

class ParameterBuilder:
    def __init__(self, uid, auth_key, secret_key):
        self.uid = uid
        self.auth_key = auth_key
        self.secret_key = secret_key
        self.content = ''
        self.parameter_list = []

    def add_parameter(self, key, value):
        self.parameter_list.append((key, value))

    def build(self):
        self.parameter_list.sort(key=lambda tup: tup[0])
        temp = ''
        for first, second in self.parameter_list:
            if temp:
                temp += '&'
                self.content += '&'
            escaped_key = quote_plus(first)
            if not second:
                temp += first + '='
                self.content += escaped_key + '='
            else:
                escaped_value = quote_plus(second)
                temp += first + '=' + second
                self.content += escaped_key + '=' + escaped_value

        temp += ':' + self.secret_key
        self.content += '&authCode=' + \
            quote_plus(base64.b64encode(
                hashlib.sha1(temp.encode('utf-8')).digest()).decode())

        return self.content
    
class EventMission:
    def __init__(self, message, progressFrom, progressTo, condition):
        self.message = message
        self.progressFrom = progressFrom
        self.progressTo = progressTo
        self.condition = condition


class gachaInfoServant:
    def __init__(self, isNew, objectId, sellMana, sellQp):
        self.isNew = isNew
        self.objectId = objectId
        self.sellMana = sellMana
        self.sellQp = sellQp

def top_login(user_id, auth_key, secret_key):
    game_data = get_latest_game_data()
    
    builder = ParameterBuilder(user_id, auth_key, secret_key)
    builder.add_parameter('appVer', APP_VER)
    builder.add_parameter('authKey', auth_key)
    builder.add_parameter('dataVer', str(game_data['data_ver']))
    builder.add_parameter('dateVer', str(game_data['date_ver']))
    builder.add_parameter('idempotencyKey', str(uuid.uuid4()))
    builder.add_parameter('lastAccessTime', get_time_stamp())
    builder.add_parameter('userId', user_id)
    builder.add_parameter('verCode', VER_CODE)
    if REGION == "NA":
        builder.add_parameter('country', '36')

    with open('private_key.pem', 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend())

    idk = builder.parameter_list[4][1]
    input_string = f"{user_id}{idk}"
    signature = private_key.sign(
        input_string.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    idempotency_key_signature = base64.b64encode(signature).decode('utf-8')
    last_access_time = builder.parameter_list[5][1]
    user_state = (-int(last_access_time) >> 2) ^ int(user_id) & game_data['asset_bundle']['folderCrc']

    builder.add_parameter('assetbundleFolder', game_data['asset_bundle']['folderName'])
    
    builder.add_parameter('deviceInfo', DEVICE_INFO)
    builder.add_parameter('isTerminalLogin', '1')
    builder.add_parameter('userState', str(user_state))
    if REGION == "JP":
        builder.add_parameter('idempotencyKeySignature', idempotency_key_signature)

    url = f'{SERVER_ADDR}/login/top?_userId={user_id}'
    data = builder.build()
    headers = {
        'User-Agent': USER_AGENT,
        'Accept-Encoding': "deflate, gzip",
        'Content-Type': "application/x-www-form-urlencoded",
        'X-Unity-Version': "2022.3.28f1"
    }
    response = requests.post(url, data=data, headers=headers, verify=True)
    return response.json()


def decode_certificate(certificate):
    cert_byte = base64.b64decode(certificate)
    key = "b5nHjsMrqaeNliSs3jyOzgpD".encode('utf-8')
    iv = "wuD6keVr".encode('utf-8')
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    result = cipher.decrypt(cert_byte)
    json_end = result.rfind(b'}') + 1
    json_data = result[:json_end].decode('utf-8')
    
    try:
        parsed_json = json.loads(json_data)
        user_id = parsed_json["userId"]
        auth_key = parsed_json["authKey"]
        secret_key = parsed_json["secretKey"]
        
        return user_id, auth_key, secret_key
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None, None, None

def login(cert):
    user_id, auth_key, secret_key = decode_certificate(cert)
    if user_id and auth_key and secret_key:
        data = top_login(user_id, auth_key, secret_key)
        name = data['cache']['replaced']['userGame'][0]['name']
        stone = data['cache']['replaced']['userGame'][0]['stone']
        lv = data['cache']['replaced']['userGame'][0]['lv']
        ticket = 0
        goldenfruit = 0
        silverfruit = 0
        bronzefruit = 0
        bluebronzesapling = 0
        bluebronzefruit = 0
        pureprism = 0
        sqf01 = 0
        holygrail = 0

        for item in data['cache']['replaced']['userItem']:
            if item['itemId'] == 4001:
                ticket = item['num']
                break
        
        for item in data['cache']['replaced']['userItem']:
            if item['itemId'] == 100:
                goldenfruit = item['num']
                break

        for item in data['cache']['replaced']['userItem']:
            if item['itemId'] == 101:
                silverfruit = item['num']
                break

        for item in data['cache']['replaced']['userItem']:
            if item['itemId'] == 102:
                bronzefruit = item['num']
                break

        for item in data['cache']['replaced']['userItem']:
            if item['itemId'] == 103:
                bluebronzesapling = item['num']
                break

        for item in data['cache']['replaced']['userItem']:
            if item['itemId'] == 104:
                bluebronzefruit = item['num']
                break

        for item in data['cache']['replaced']['userItem']:
            if item['itemId'] == 46:
                pureprism = item['num']
                break

        for item in data['cache']['replaced']['userItem']:
            if item['itemId'] == 16:
                sqf01 = item['num']
                break

        for item in data['cache']['replaced']['userItem']:
            if item['itemId'] == 7999:
                holygrail = item['num']
                break
        
        login_days = data['cache']['updated']['userLogin'][0]['seqLoginCount']
        total_days = data['cache']['updated']['userLogin'][0]['totalLoginCount']
        fpids1 = data['cache']['replaced']['userGame'][0]['friendCode']
        act_max = data['cache']['replaced']['userGame'][0]['actMax']
        act_recover_at = data['cache']['replaced']['userGame'][0]['actRecoverAt']
        carryOverActPoint = data['cache']['replaced']['userGame'][0]['carryOverActPoint']
        serverTime = data['cache']['serverTime']
        ap_points = act_recover_at - serverTime
        remaining_ap = 0

        if ap_points > 0:
            lost_ap_point = (ap_points + 299) // 300
            if act_max >= lost_ap_point:
                remaining_ap_int = act_max - lost_ap_point
                remaining_ap = int(remaining_ap_int)
        else:
            remaining_ap = act_max + carryOverActPoint
        
        now_act = (act_max - (act_recover_at - GetTimeStamp()) / 300)

        add_fp = data['response'][0]['success']['addFriendPoint']
        total_fp = data['cache']['replaced']['tblUserGame'][0]['friendPoint']

        bonus_message = None
        items = []
        bonus_name = None
        bonus_detail = None
        items_camp_bonus = []

        if 'seqLoginBonus' in data['response'][0]['success']:
            bonus_message = data['response'][0]['success']['seqLoginBonus'][0]['message']

            for i in data['response'][0]['success']['seqLoginBonus'][0]['items']:
                items.append(f'{i["name"]} x{i["num"]}')

            if 'campaignbonus' in data['response'][0]['success']:
                bonus_name = data['response'][0]['success']['campaignbonus'][0]['name']
                bonus_detail = data['response'][0]['success']['campaignbonus'][0]['detail']

                for i in data['response'][0]['success']['campaignbonus'][0]['items']:
                    items_camp_bonus.append(f'{i["name"]} x{i["num"]}')

        result = {
            "Name": name,
            "Level": lv,
            "Stone": stone,
            "Ticket": ticket,
            "Golden Fruit": goldenfruit,
            "Silver Fruit": silverfruit,
            "Bronze Fruit": bronzefruit,
            "Blue Bronze Sapling": bluebronzesapling,
            "Blue Bronze Fruit": bluebronzefruit,
            "Pure Prism": pureprism,
            "SQ Fragments": sqf01,
            "Holy Grail": holygrail,
            "Login Days": login_days,
            "Total Days": total_days,
            "Friend Code": fpids1,
            "Max Action Points": act_max,
            "Action Points Recovery Time": act_recover_at,
            "Carry Over Action Points": carryOverActPoint,
            "Server Time": serverTime,
            "Remaining Action Points": remaining_ap,
            "Current Action Points": now_act,
            "Additional Friend Points": add_fp,
            "Total Friend Points": total_fp,
            "Bonus": [
                {"Message bonus": bonus_message},
                {"Message item": items},
                {"Campaign Bonus Name": bonus_name},
                {"Campaign Bonus Detail": bonus_detail},
                {"Campaign Bonus Items": items_camp_bonus}
            ]
        }

        return result
    else:
        print("Failed to decode certificate.")
        return None

def GetGachaSubIdFP(region = REGION):
    response = requests.get(f"https://git.atlasacademy.io/atlasacademy/fgo-game-data/raw/branch/{region}/master/mstGachaSub.json");
    gachaList = json.loads(response.text)
    timeNow = GetTimeStamp()
    priority = 0
    goodGacha = {}
    for gacha in gachaList:
        openedAt = gacha["openedAt"]
        closedAt = gacha["closedAt"]

        if openedAt <= timeNow & timeNow <= closedAt:
            p = int(gacha["priority"])
            if(p > priority):
                priority = p
                goodGacha = gacha
    return str(goodGacha["id"])

def drawFP(auth_key, user_id, secret_key):
    game_data = get_latest_game_data()
    data = top_login(user_id, auth_key, secret_key)
    gachaSubId = GetGachaSubIdFP()

    if gachaSubId is None:
        gachaSubId = "0"
    
    builder = ParameterBuilder(user_id, auth_key, secret_key)
    builder.add_parameter('storyAdjustIds', '[]')
    builder.add_parameter('selectBonusList', '')
    builder.add_parameter('authKey', auth_key)
    builder.add_parameter('appVer', APP_VER)
    builder.add_parameter('dateVer', str(game_data['date_ver']))
    builder.add_parameter('lastAccessTime', get_time_stamp())
    builder.add_parameter('verCode', VER_CODE)
    builder.add_parameter('idempotencyKey', str(uuid.uuid4()))
    builder.add_parameter('gachaId', '1')
    builder.add_parameter('num', '10')
    builder.add_parameter('ticketItemId', '0')
    builder.add_parameter('shopIdIndex', '1')
    builder.add_parameter('gachaSubId', gachaSubId)
    builder.add_parameter('userId', user_id)
    builder.add_parameter('dataVer', str(game_data['data_ver']))

    url = f'{SERVER_ADDR}/gacha/draw?_userId={user_id}'
    param = builder.build()
    headers = {
        'User-Agent': USER_AGENT,
        'Accept-Encoding': "deflate, gzip",
        'Content-Type': "application/x-www-form-urlencoded",
        'X-Unity-Version': "2022.3.28f1"
    }
    response = requests.post(url, data=param, headers=headers, verify=True)
    data = response.json()
    responses = data['response']

    servantArray = []
    missionArray = []

    for response in responses:
        resCode = response['resCode']
        resSuccess = response['success']

        if (resCode != "00"):
            continue

        if "gachaInfos" in resSuccess:
            for info in resSuccess['gachaInfos']:
                servantArray.append(
                    gachaInfoServant(
                        info['isNew'], info['objectId'], info['sellMana'], info['sellQp']
                    )
                )

        if "eventMissionAnnounce" in resSuccess:
            for mission in resSuccess["eventMissionAnnounce"]:
                missionArray.append(
                    EventMission(
                        mission['message'], mission['progressFrom'], mission['progressTo'], mission['condition']
                    )
                )
    return servantArray, missionArray

    
def buyBlueApple(user_id, auth_key, secret_key):
    if os.environ.get("BUY_BLUE_APPLE") != "Y":
        print("BUY_BLUE_APPLE secret is set to N. Skipping.")
        return
    game_data = get_latest_game_data()
    data = top_login(user_id, auth_key, secret_key)
    
    actRecoverAt = data['cache']['replaced']['userGame'][0]['actRecoverAt']
    actMax = data['cache']['replaced']['userGame'][0]['actMax']
    carryOverActPoint = data['cache']['replaced']['userGame'][0]['carryOverActPoint']
    serverTime = data['cache']['serverTime']

    bluebronzesapling = 0 
    for item in data['cache']['replaced']['userItem']:
        if item['itemId'] == 103:
            bluebronzesapling = item['num']
            break
        
    ap_points = actRecoverAt - serverTime
    remaining_ap = 0

    if ap_points > 0:
       lost_ap_point = (ap_points + 299) // 300
       if actMax >= lost_ap_point:
           remaining_ap = actMax - lost_ap_point
           remaining_ap_int = int(remaining_ap)
    else:
        remaining_ap = actMax + carryOverActPoint
        remaining_ap_int = int(remaining_ap)

    if bluebronzesapling > 0:
        quantity = remaining_ap_int // 40
        if quantity == 0:
            print(f"\n ======================================== \n Not enough AP to exchange blue apple \n ======================================== ")
            return
        
        if bluebronzesapling < quantity:
            num_to_purchase = bluebronzesapling
        else:
            num_to_purchase = quantity

        builder = ParameterBuilder(user_id, auth_key, secret_key)
        builder.add_parameter('userId', user_id)
        builder.add_parameter('authKey', auth_key)
        builder.add_parameter('appVer', APP_VER)
        builder.add_parameter('dateVer', str(game_data['date_ver']))
        builder.add_parameter('lastAccessTime', get_time_stamp())
        builder.add_parameter('verCode', VER_CODE)
        builder.add_parameter('idempotencyKey', str(uuid.uuid4()))
        builder.add_parameter('id', '13000000')
        builder.add_parameter('num', str(num_to_purchase))
        builder.add_parameter('dataVer', str(game_data['data_ver']))
            
        url = f'{SERVER_ADDR}/shop/purchase?_userId={user_id}'
        data = builder.build()
        headers = {
            'User-Agent': USER_AGENT,
            'Accept-Encoding': "deflate, gzip",
            'Content-Type': "application/x-www-form-urlencoded",
            'X-Unity-Version': "2022.3.28f1"
        }
        response = requests.post(url, data=data, headers=headers, verify=True)
        data = response.json()

        responses = data['response']

        for response in responses:
            resCode = response['resCode']
            resSuccess = response['success']
            nid = response["nid"]

            if (resCode != "00"):
                continue

            if nid == "purchase":
                if "purchaseName" in resSuccess and "purchaseNum" in resSuccess:
                    purchaseName = resSuccess['purchaseName']
                    purchaseNum = resSuccess['purchaseNum']

                    print(f"\n========================================\n[+] {purchaseNum}x {purchaseName} Purchase Success\n========================================")
                    return {"item": purchaseName, "num": purchaseNum}
    else:
        print(f"\n ======================================== \n Not enough saplings \n ======================================== " )

def discord_webhook(data):
    url = os.environ.get("webhookDiscord")
    messageBonus = ''
    nl = '\n'

    if "No Bonus" in data["Bonus"]:
        messageBonus = ""
    else:
        bonuses = data["Bonus"]
        
        if bonuses:
            if bonuses[0].get("Message bonus"):
                messageBonus += f"__{bonuses[0]['Message bonus']}__{nl}```{nl.join(bonuses[0].get('Message Items', []))}```"
            
            if bonuses[0].get("Campaign Bonus Name"):
                messageBonus += f"{nl}__{bonuses[0]['Campaign Bonus Name']}__{nl}{bonuses[0].get('Campaign Bonus Detail', '')}{nl}```{nl.join(bonuses[0].get('Campaign Bonus Items', []))}```"

    if url:
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
        "content": None,
        "embeds": [
            {
                "title": "FGO Daily Login - " + REGION,
                "description": f"Succesfully login.\n\n{messageBonus}",
                "color": 563455,
                    "fields": [
                {
                "name": "Master Name",
                "value": f"{data['Name']}",
                "inline": True
                },
                {
                "name": "Friend ID",
                "value": f"{data['Friend Code']}",
                "inline": True
                },
                {
                "name": "Level",
                "value": f"{data['Level']}",
                "inline": True
                },
                {
                "name": "Summon Tickets", 
                "value": f"{data['Ticket']}",
                "inline": True
                },                    
                {
                "name": "Saint Quartz",
                "value": f"{data['Stone']}",
                "inline": True
                },
                {
                "name": "SQ Fragments",
                "value": f"{data['SQ Fragments']}",
                "inline": True
                },
                {
                "name": "Golden Apples",
                "value": f"{data['Golden Fruit']}",
                "inline": True
                },
                {
                "name": "Silver Apples",
                "value": f"{data['Silver Fruit']}",
                "inline": True
                },
                {
                "name": "Bronze Apples",
                "value": f"{data['Bronze Fruit']}",
                "inline": True
                },
                {
                "name": "Blue Apples",
                "value": f"{data['Blue Bronze Fruit']}",
                "inline": True
                },
                {
                "name": "Blue Apple Saplings",
                "value": f"{data['Blue Bronze Sapling']}",
                "inline": True
                },
                {
                "name": "Consecutive Login Days",
                "value": f"{data['Login Days']}",
                "inline": True
                },
                {
                "name": "Total Login Days",
                "value": f"{data['Total Days']}",
                "inline": True
                },
                {
                "name": "Pure Prism",
                "value": f"{data['Pure Prism']}",
                "inline": True
                },
                {
                "name": "FP",
                "value": f"{data['Total Friend Points']}",
                "inline": True
                },
                {
                "name": "FP Obtained Today",
                "value": f"{data['Additional Friend Points']}",
                "inline": True
                },
                {
                "name": "Current AP",
                "value": f"{data['Current Action Points']}",
                "inline": True
                },
                {
                "name": "Holy Grails",
                "value": f"{data['Holy Grail']}",
                "inline": True
                },
                
            ],
                "thumbnail": {
                    "url": "https://www.fate-go.jp/manga_fgo/images/commnet_chara01.png"
                }
            }
        ],
        "attachments": []
    }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Error: {e}")        
            
    else:
        print("DISCORD_WEBHOOK is not set.")

def main():
    your_certificate = os.environ.get("CERT")

    if ";" not in your_certificate:
        try:
            user_id, auth_key, secret_key = decode_certificate(your_certificate)
            if user_id and auth_key and secret_key:
                try_login = login(your_certificate)
                if try_login:
                    discord_webhook(try_login)
                    print(f"Name: {try_login['Name']}")
                    print(f"Login Days: {try_login['Login Days']}/")
                    formatted_message = '\n'.join(
                        '\n'.join(f"{key}: {value}" for key, value in bonus.items())
                        for bonus in try_login['Bonus']
                    )
                    print(f"Message:\n{formatted_message}")
                    drawFP(auth_key, user_id, secret_key)
                    
                bba = buyBlueApple(user_id, auth_key, secret_key)
                if bba:
                    print(f"\nConsume {40 * bba['num']}Ap, Exchange {bba['num']}x {bba['num']} ")

        except Exception as e:
            print(f"Error: {e}")
        return
    
    else:
        auth_key = your_certificate.split(";")
        
        for cert in auth_key:
            try: 
                user_id, auth_key, secret_key = decode_certificate(cert)
                if user_id and auth_key and secret_key:
                    try_login = login(cert)
                    if try_login:
                        discord_webhook(try_login)
                        print(f"======\nName: {try_login['Name']}")
                        print(f"Login Days: {try_login['Login Days']}")
                        formatted_message = '\n'.join(
                            '\n'.join(f"{key}: {value}" for key, value in bonus.items())
                            for bonus in try_login['Bonus']
                        )
                        print(f"Message:\n{formatted_message}")
                        dfp = drawFP(auth_key, user_id, secret_key)
                        if dfp:
                            print(f"\nDraw {len(dfp[0])} Servants")
                        
                        bba = buyBlueApple(user_id, auth_key, secret_key)
                        if bba:
                            print(f"\nConsume {40 * bba['num']}Ap, Exchange {bba['num']}x {bba['num']} ")

            except Exception as e:
                print(f"Error: {e}")

        return

if __name__ == "__main__":
    main()
