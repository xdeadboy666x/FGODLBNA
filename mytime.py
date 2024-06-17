from datetime import datetime, timedelta, timezone

tz_utc_minus_7 = timezone(timedelta(hours=-7))

def GetNowTimeHour():
    return datetime.now(tz=tz_utc_minus_7).hour

def GetNowTime():
    return datetime.now(tz=tz_utc_minus_7)

def GetFormattedNowTime():
    return datetime.now(tz=tz_utc_minus_7).strftime('%Y-%m-%d %H:%M:%S')

def GetTimeStamp():
    return int(datetime.now(tz=tz_utc_minus_7).timestamp())

def TimeStampToString(timestamp):
    return datetime.fromtimestamp(timestamp, tz=tz_utc_minus_7)

def GetNowTimeFileName():
    return datetime.now(tz=tz_utc_minus_7).strftime('%Y/%m/%d.log')