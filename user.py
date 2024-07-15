import json
import hashlib
import base64
import uuid
from urllib.parse import quote_plus

class ParameterBuilder:
    def __init__(self, uid: str, auth_key: str, secret_key: str):
        self.uid_ = uid
        self.auth_key_ = auth_key
        self.secret_key_ = secret_key
        self.content_ = ''
        self.parameter_list_ = [
            ('appVer', fgourl.app_ver_),
            ('authKey', self.auth_key_),
            ('dataVer', str(fgourl.data_ver_)),
            ('dateVer', str(fgourl.date_ver_)),
            ('idempotencyKey', str(uuid.uuid4())),
            ('lastAccessTime', str(mytime.GetTimeStamp())),
            ('userId', self.uid_),
            ('verCode', fgourl.ver_code_),
        ]

    def add_parameter(self, key: str, value: str):
        self.parameter_list_.append((key, value))

    def build(self) -> str:
        self.parameter_list_.sort(key=lambda tup: tup[0])
        temp = ''
        for first, second in self.parameter_list_:
            if temp:
                temp += '&'
                self.content_ += '&'
            escaped_key = quote_plus(first)
            if not second:
                temp += first + '='
                self.content_ += escaped_key + '='
            else:
                escaped_value = quote_plus(second)
                temp += first + '=' + second
                self.content_ += escaped_key + '=' + escaped_value

        temp += ':' + self.secret_key_
        self.content_ += '&authCode=' + quote_plus(base64.b64encode(hashlib.sha1(temp.encode('utf-8')).digest()))

        return self.content_

    def clean(self):
        self.content_ = ''
        self.parameter_list_ = [
            ('appVer', fgourl.app_ver_),
            ('authKey', self.auth_key_),
            ('dataVer', str(fgourl.data_ver_)),
            ('dateVer', str(fgourl.date_ver_)),
            ('idempotencyKey', str(uuid.uuid4())),
            ('lastAccessTime', str(mytime.GetTimeStamp())),
            ('userId', self.uid_),
            ('verCode', fgourl.ver_code_),
        ]

class Rewards:
    def __init__(self, stone, level, ticket, goldenfruit, silverfruit, bronzefruit, bluebronzesapling, bluebronzefruit, pureprism, sqf01, holygrail):
        self.stone = stone
        self.level = level
        self.ticket = ticket
        self.goldenfruit = goldenfruit
        self.silverfruit = silverfruit
        self.bronzefruit = bronzefruit
        self.bluebronzesapling = bluebronzesapling
        self.bluebronzefruit = bluebronzefruit
        self.pureprism = pureprism
        self.sqf01 = sqf01
        self.holygrail = holygrail

class Login:
    def __init__(self, name, login_days, total_days, act_max, act_recover_at, now_act, add_fp, total_fp):
        self.name = name
        self.login_days = login_days
        self.total_days = total_days
        self.act_max = act_max
        self.act_recover_at = act_recover_at
        self.now_act = now_act
        self.add_fp = add_fp
        self.total_fp = total_fp

class Bonus:
    def __init__(self, message, items, bonus_name, bonus_detail, bonus_camp_items):
        self.message = message
        self.items = items
        self.bonus_name = bonus_name
        self.bonus_detail = bonus_detail
        self.bonus_camp_items = bonus_camp_items

class User:
    def __init__(self, user_id: str, auth_key: str, secret_key: str):
        self.name_ = ''
        self.user_id_ = int(user_id)
        self.s_ = fgourl.NewSession()
        self.builder_ = ParameterBuilder(user_id, auth_key, secret_key)

    def post(self, url):
        res = fgourl.PostReq(self.s_, url, self.builder_.build())
        self.builder_.clean()
        return res

    def parse_items(self, items):
        parsed_items = {
            4001: 0, 100: 0, 101: 0, 102: 0, 103: 0, 104: 0, 46: 0, 16: 0, 7999: 0
        }
        for item in items:
            if item['itemId'] in parsed_items:
                parsed_items[item['itemId']] = item['num']
        return parsed_items

    def top_login(self):
        DataWebhook = []  # This data will be used in the discord webhook!

        lastAccessTime = self.builder_.parameter_list_[5][1]
        userState = (-int(lastAccessTime) >> 2) ^ self.user_id_ & fgourl.data_server_folder_crc_

        self.builder_.add_parameter('assetbundleFolder', fgourl.asset_bundle_folder_)
        self.builder_.add_parameter('deviceInfo', 'HUAWEI MAR-LX3Bm / Android OS 10 / API-29 (MAR-L03B 10.0.0.274(C69E7R1P1)/10.0.0.274C69)')
        self.builder_.add_parameter('isTerminalLogin', '1')
        self.builder_.add_parameter('userState', str(userState))

        data = self.post(f'{fgourl.server_addr_}/login/top?_userId={self.user_id_}')

        with open('login.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        user_game = data['cache']['replaced']['userGame'][0]
        user_items = data['cache']['replaced']['userItem']

        self.name_ = hashlib.md5(user_game['name'].encode('utf-8')).hexdigest()
        parsed_items = self.parse_items(user_items)

        rewards = Rewards(
            user_game['stone'], user_game['lv'], parsed_items[4001], parsed_items[100], parsed_items[101],
            parsed_items[102], parsed_items[103], parsed_items[104], parsed_items[46], parsed_items[16], parsed_items[7999]
        )

        DataWebhook.append(rewards)

        user_login = data['cache']['updated']['userLogin'][0]
        act_max = user_game['actMax']
        act_recover_at = user_game['actRecoverAt']
        now_act = act_max - (act_recover_at - mytime.GetTimeStamp()) / 300

        login = Login(
            self.name_, user_login['seqLoginCount'], user_login['totalLoginCount'], act_max, act_recover_at,
            now_act, data['response'][0]['success']['addFriendPoint'], data['cache']['replaced']['tblUserGame'][0]['friendPoint']
        )

        DataWebhook.append(login)

        if 'seqLoginBonus' in data['response'][0]['success']:
            seq_login_bonus = data['response'][0]['success']['seqLoginBonus'][0]
            bonus_message = seq_login_bonus['message']
            items = [f'{i["name"]} x{i["num"]}' for i in seq_login_bonus['items']]

            if 'campaignbonus' in data['response'][0]['success']:
                campaign_bonus = data['response'][0]['success']['campaignbonus'][0]
                bonus_name = campaign_bonus['name']
                bonus_detail = campaign_bonus['detail']
                items_camp_bonus = [f'{i["name"]} x{i["num"]}' for i in campaign_bonus['items']]
            else:
                bonus_name = None
                bonus_detail = None
                items_camp_bonus = []

            bonus = Bonus(bonus_message, items, bonus_name, bonus_detail, items_camp_bonus)
            DataWebhook.append(bonus)
        else:
            DataWebhook.append("No Bonus")

        webhook.topLogin(DataWebhook)

    def buy_blue_apple(self, quantity=1):
        # https://game.fate-go.jp/shop/purchase
        self.builder_.add_parameter('id', '13000000')
        self.builder_.add_parameter('quantity', str(quantity))
        data = self.post(f'{fgourl.server_addr_}/shop/purchase')
        return data