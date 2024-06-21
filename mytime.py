from datetime import datetime, timedelta, timezone

tz_gmt_9 = timezone(timedelta(hours=9))  # Change timezone offset to GMT+9

def GetNowTimeHour():
    return datetime.now(tz=tz_gmt_9).hour

def GetNowTime():
    return datetime.now(tz=tz_gmt_9)

def GetFormattedNowTime():
    return datetime.now(tz=tz_gmt_9).strftime('%Y-%m-%d %H:%M:%S')

def GetTimeStamp():
    return int(datetime.now(tz=tz_gmt_9).timestamp())

def TimeStampToString(timestamp):
    return datetime.fromtimestamp(timestamp, tz=tz_gmt_9)

def GetNowTimeFileName():
    return datetime.now(tz=tz_gmt_9).strftime('%Y/%m/%d.log')
