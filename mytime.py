import math
from datetime import datetime, timedelta, timezone

# Set timezone to UTC+9
tz_utc_9 = timezone(timedelta(hours=9))

class MyTime:
    @classmethod
    def get_timestamp(cls):
        return int(datetime.now().timestamp())  # FGO uses UTC time

    @classmethod
    def is_Free_FP_draw_available(cls, last_free_draw_timestamp_utc: int):
        JST = timezone(timedelta(hours=+9))
        # get last free draw time in GMT+0 and convert to GMT+9 to the next day
        dt_utc = datetime.fromtimestamp(last_free_draw_timestamp_utc, timezone.utc)
        dt_japan = dt_utc.astimezone(JST)
        next_midnight = datetime(dt_japan.year, dt_japan.month, dt_japan.day, tzinfo=JST) + timedelta(days=1)

        # Convert next_midnight back to UTC to compare with the current time
        next_midnight_utc = next_midnight.astimezone(timezone.utc)
        next_midnight_timestamp = next_midnight_utc.timestamp()

        # Returns True if the current time has passed the midnight of the day following the last draw date
        return cls.get_timestamp() >= next_midnight_timestamp

    @classmethod
    def get_used_act_ammount(cls, full_recover_at: int):
        return max(0, math.ceil((full_recover_at - cls.get_timestamp()) / 300))

# Existing functions with timezone set to UTC+9
def GetNowTimeHour():
    return datetime.now(tz=tz_utc_9).hour

def GetNowTime():
    return datetime.now(tz=tz_utc_9)

def GetFormattedNowTime():
    return datetime.now(tz=tz_utc_9).strftime('%Y-%m-%d %H:%M:%S')

def GetTimeStamp():
    return int(datetime.now(tz=tz_utc_9).timestamp())

def TimeStampToString(timestamp):
    return datetime.fromtimestamp(timestamp, tz=tz_utc_9).strftime('%Y-%m-%d %H:%M:%S')

def GetNowTimeFileName():
    return datetime.now(tz=tz_utc_9).strftime('%Y/%m/%d.log')
