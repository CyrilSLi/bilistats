# Built-in modules
import json, os, time, random, subprocess
from datetime import timedelta

# Third-party modules
import requests as r
from dotenv import load_dotenv
from slack_sdk import WebClient

load_dotenv ()
token = os.environ.get('SLACK_USER_TOKEN')
if not token:
    raise SystemExit ("Please set SLACK_USER_TOKEN to a Slack user token with status read & write permissions")
sessdata = os.environ.get('BILIBILI_SESSDATA')
if not sessdata:
    raise SystemExit ("Please set BILIBILI_SESSDATA to your Bilibili SESSDATA cookie")
client = WebClient (token = token)

def set_status (status_text, status_emoji = None):
    try:
        response = client.users_profile_set (
            profile = {
                "status_text": status_text,
                "status_emoji": status_emoji if status_emoji else ""
            }
        )
        if response ["ok"]:
            return True
        else:
            print (f"Error updating status: {response ['error']}")
            return False
    except Exception as e:
        print (f"An error occurred: {e}")
        return False

def get_status ():
    try:
        response = client.users_profile_get ()
        if response ["ok"]:
            return (response ["profile"] ["status_text"], response ["profile"] ["status_emoji"])
        else:
            print (f"Error getting status: {response ['error']}")
    except Exception as e:
        print (f"An error occurred: {e}")
        return (None, None)

def get_video ():
    try:
        history = subprocess.run (["curl", "-G", "https://api.bilibili.com/x/web-interface/history/cursor", "--data-urlencode", "ps=1", "-b", f"SESSDATA={sessdata}"], capture_output = True)
        history.check_returncode ()
        history = json.loads (history.stdout.decode ())
        history = history ["data"] ["list"] [0]
    except Exception as e:
        print (f"An error occurred: {e}")
        return False

    ts = history ["view_at"]
    if ts > int (time.time ()) - 30:
        return (history ["title"], int (history ["progress"]), int (history ["duration"]))
    else:
        return False

if __name__ == "__main__":
    orig_text, orig_emoji = get_status ()
    print ("Original status:", orig_emoji, orig_text)
    try:
        while True:
            video = get_video ()
            if video:
                status_text = f"{video[0]}\n({timedelta (seconds = video [1])} / {timedelta (seconds = video [2])})".replace (":", "\u2236")
                status_emoji = ":bilibili:" # Replace with another emoji if desired
            else:
                status_text, status_emoji = orig_text, orig_emoji
            set_status (status_text, status_emoji)
            print (f"{int (time.time ())}\t{status_emoji}\t{repr (status_text)}")
            time.sleep (random.randint (45, 60)) # Introduces some randomness, hopefully avoiding rate limiting
    except BaseException as e:
        print ("An exception occurred:", e)
        print ("Exiting...")
        set_status (orig_text, orig_emoji)
        raise SystemExit
