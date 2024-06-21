from datetime import datetime, timedelta, timezone

tz_gmt_8 = timezone(timedelta(hours=-8))  # Change timezone offset to GMT-8

def GetNowTimeHour():
    return datetime.now(tz=tz_gmt_8).hour

def GetNowTime():
    return datetime.now(tz=tz_gmt_8)

def GetFormattedNowTime():
    return datetime.now(tz=tz_gmt_8).strftime('%Y-%m-%d %H:%M:%S')

def GetTimeStamp():
    return int(datetime.now(tz=tz_gmt_8).timestamp())

def TimeStampToString(timestamp):
    return datetime.fromtimestamp(timestamp, tz=tz_gmt_8)

def GetNowTimeFileName():
    return datetime.now(tz=tz_gmt_8).strftime('%Y/%m/%d.log')
