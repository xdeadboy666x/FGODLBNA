from datetime import datetime, timedelta, timezone

tz_game_server = timezone(timedelta(hours=9))

def GetNowTimeHour():
    return datetime.now(tz=tz_game_server).hour

def GetNowTime():
    return datetime.now(tz=tz_game_server)

def GetFormattedNowTime():
    return datetime.now(tz=tz_game_server).strftime('%Y-%m-%d %H:%M:%S')

def GetTimeStamp():
    return int(datetime.now(tz=tz_game_server).timestamp())

def TimeStampToString(timestamp):
    return datetime.fromtimestamp(timestamp, tz=tz_game_server)

def GetNowTimeFileName():
    return datetime.now(tz=tz_game_server).strftime('%Y/%m/%d.log')