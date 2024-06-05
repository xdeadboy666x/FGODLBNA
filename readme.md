
<img width="50%" style="border: 1px solid black" src="https://i.imgur.com/azBO1qu.png">

# # Fate/Grand Order Auto-Login System

🤓 Use at your own risk. 👌

🫠 Note: You need to update this library every 60 days for timed login to take effect. This is required for the GitHub automated process. 🫠

✅ **Author:** [O-Isaac](https://github.com/O-Isaac/FGO-Daily-Login)

This FGO auto-login system is based on the mod for the project [FGODailyBonus](https://github.com/hexstr/FGODailyBonus).

## Features:
- No logging
- Automatic game version update synchronization
- Sends login results and more to your Discord channel
- JP version only

## Extract Your Game Account Data
To perform this operation, you will need to extract your account data. It's very simple: use a file manager to navigate to the following path and obtain the specified files (ROOT may be required):

| Version | Path | File Name |
| --- | --- | --- | 
| JP | `android/data/com.aniplex.fategrandorder/files/data/` | 54cc790bf952ea710ed7e8be08049531 |

# # Decrypting Your Account Data

Please handle this data with utmost care. Do not share it with others, as it is sensitive information that communicates directly with the server and could be used to steal your number!

1. Download FGO-ADET, review the decryption method, and decrypt the file: [FGO-ADET](https://github.com/DNNDHH/FGO-ADET)
2. Retrieve the user agent of your device (phone or emulator) from [this site](https://www.whatismybrowser.com/detect/what-is-my-user-agent/)

# Creating a Discord Message Notification Bot

To create a Discord webhook, follow these steps:

1. Create a server in Discord.
2. Create a text channel in the server.
3. In the channel's settings, navigate to `Integrations` > `Webhook` > `Create`. webhook > copy url webhook`

# ## Performing Timed Check-in Tasks / Timed Logins

Timed check-ins for FGO are based on [UTC time](https://time.is/compare/utc/local).

| ## Version | Auto-Login Time
|--------|-------------|
| JP | 30 19 * * * |

🫠 The code format `30 19 * * *` refers to 19:30 UTC time. For reference, please check your current [UTC time](https://time.is/compare/utc/local).

To modify the auto-login process and adjust the auto-login time, please refer to [this link](https://github.com/DNNDHH/F-D-L/blob/master/.github/workflows/run.yml).
 ```console
  schedule:
    - cron: "00 03 * * *"
    - cron: "30 03 * * *"
    - cron: "30 13 * * *"
    - cron: "30 17 * * *"
  ```  


# ## Entering the Game Account Key and Configuring POST Requests

To set up the game account key and configure POST requests, follow these steps:

`Top Right > Settings > Secrets and Variables > Actions`

<img width="75%" style="border: 1px solid black" src="https://i.imgur.com/J7jb6TX.png">

Use a comma if you need to log in to multiple accounts. 

```console
,
```console
,
  ```

| Key type | Account keys sample |
| --- | --- |
| GAME_AUTHKEYS | RaNdOmStRiNg1234:randomAAAAA=,RaNdOmStRiNg1235:randomAAAAA= |
| GAME_SECRETKEYS | RaNdOmStRiNg1234:randomAAAAA=,RaNdOmStRiNg1235:randomAAAAA= |
| GAME_USERIDS | 1234,1235 |
| GAME_REGION | JP |
| GAME_USERAGENT | Dalvik/2.1.0 (Linux; U; Android 14; Pixel 5 Build/UP1A.231105.001) It is not recommended to change this, but if you decide to do so, you will also need to update the [Device Information].(https://github.com/DNNDHH/F-D-L/commit/2dbe2ac8403802d676a69aeb874fedd932ae98e7) |
| DISCORD_WEBHOOK | https://discord.com/api/webhooks/randomNumber/randomString |

# ## Completed
- [x] Automatic Daily Friendship Point Summoning
- [x] Automatic Blue Apple Planting 🍎
- [x] Automatic Gift Box Collection

## Future Plans (coo coo coo 🤣)
- [ ] What features would you like to see? You name it...

## Appreciation
- [hexstr](https://github.com/hexstr), author of the FGO Auto Login System.