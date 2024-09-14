import math
from datetime import datetime, timedelta, timezone


def GetNowTimeHour():
    return datetime.now(tz=tz_utc_8).hour


def GetNowTime():
    return datetime.now(tz=tz_utc_8)


def GetFormattedNowTime():
    return datetime.now(tz=tz_utc_8).strftime("%Y-%m-%d %H:%M:%S")


def GetTimeStamp():
    return (int)(datetime.now(tz=tz_utc_8).timestamp())


def TimeStampToString(timestamp):
    return datetime.fromtimestamp(timestamp)


def GetNowTimeFileName():
    return datetime.now(tz=tz_utc_8).strftime("%Y/%m/%d.log")


def get_time_stamp():
    return str(int(time.time()))


def get_asset_bundle(assetbundle):
    data = base64.b64decode(assetbundle)
    key = b"nn33CYId2J1ggv0bYDMbYuZ60m4GZt5P"  # NA key
    if REGION == "JP":
        key = b"W0Juh4cFJSYPkebJB9WpswNF51oa6Gm7"  # JP key
    iv = data[:32]
    array = data[32:]
    cipher = py3rijndael.RijndaelCbc(key, iv, py3rijndael.paddings.Pkcs7Padding(16), 32)
    data = cipher.decrypt(array)
    gzip_data = gzip.decompress(data)
    data_unpacked = msgpack.unpackb(gzip_data)

    return data_unpacked
