import math
from datetime import datetime, timedelta, timezone

class MyTime:
    @classmethod
    def get_timestamp(cls):
        # Return the current UTC timestamp
        return int(datetime.now().timestamp())

    @classmethod
    def is_Free_FP_draw_available(cls, last_free_draw_timestamp_utc: int):
        JST = timezone(timedelta(hours=+9))
        # Get last free draw time in UTC and convert to JST (UTC+9) to the next day
        dt_utc = datetime.fromtimestamp(last_free_draw_timestamp_utc, timezone.utc)
        dt_japan = dt_utc.astimezone(JST)
        next_midnight = datetime(dt_japan.year, dt_japan.month, dt_japan.day, tzinfo=JST) + timedelta(days=1)

        # Convert next_midnight back to UTC to compare with the current time
        next_midnight_utc = next_midnight.astimezone(timezone.utc)
        next_midnight_timestamp = next_midnight_utc.timestamp()

        # Returns True if the current time has passed the midnight of the day following the last draw date
        return cls.get_timestamp() >= next_midnight_timestamp

    @classmethod
    def get_used_act_amount(cls, full_recover_at: int):
        # Calculate the remaining act points based on full recovery time
        return max(0, math.ceil((full_recover_at - cls.get_timestamp()) / 300))

# Example usage:
if __name__ == "__main__":
    # Simulating login response data
    login_response = {
        'cache': {
            'replaced': {
                'userGacha': [
                    {'freeDrawAt': 1622505600}  # Example timestamp for last free draw
                ]
            }
        }
    }

    # Get last free draw timestamp from login response
    last_free_draw_timestamp_utc = login_response['cache']['replaced']['userGacha'][0]['freeDrawAt']

    # Check if free FP draw is available
    is_available = MyTime.is_Free_FP_draw_available(last_free_draw_timestamp_utc)
    if is_available:
        print("Free FP draw is available. Proceed to draw.")
        # Get subId and draw logic here
    else:
        print("Next free draw time has not been reached yet. Log the next free draw time.")

    # Simulating player info data
    player_info = {
        'act_full_recover_time': 1622600000  # Example full recovery timestamp
    }

    # Calculate the used act amount
    act_now = 100  # Example current act points
    act_now = act_now - MyTime.get_used_act_amount(player_info['act_full_recover_time'])
    buy_count = int(act_now / 40)
    actual_count = 0

    blue_apple_sapling = 10  # Example count of blue apple saplings

    if blue_apple_sapling > 0:
        print("Doesn't have blue apple sapling.")
    elif blue_apple_sapling < buy_count:
        actual_count = blue_apple_sapling
        print(f"Set actual_count to blue apple sapling: {actual_count}")
    else:
        actual_count = buy_count
        print(f"Set actual_count to buy_count: {actual_count}")

    # Buy blue apples by actual_count
    print(f"Buying {actual_count} blue apples.")