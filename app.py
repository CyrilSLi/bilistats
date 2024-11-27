import json, os, time, subprocess
from datetime import timedelta

import requests as r
from slack_sdk import WebClient

token = os.environ.get('TOKEN')
sessdata = os.environ.get('SESSDATA')
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

def get_status ():
    try:
        response = client.users_profile_get ()
        if response ["ok"]:
            return (response ["profile"] ["status_text"], response ["profile"] ["status_emoji"])
        else:
            print (f"Error getting status: {response ['error']}")
    except Exception as e:
        print (f"An error occurred: {e}")

def get_video ():
    history = subprocess.run (["curl", "-G", "https://api.bilibili.com/x/web-interface/history/cursor", "--data-urlencode", "ps=1", "-b", f"SESSDATA={sessdata}"], capture_output = True)
    history.check_returncode ()
    history = json.loads (history.stdout.decode ())
    history = history ["data"] ["list"] [0]

    ts = history ["view_at"]
    if ts > int (time.time ()) - 30:
        return (history ["history"] ["part"], int (history ["progress"]), int (history ["duration"]))
    else:
        return False

if __name__ == "__main__":
    orig_text, orig_emoji = get_status ()
    try:
        while True:
            print (time.time (), "Tick")
            video = get_video ()
            if video:
                status_text = f"{video[0]} ({timedelta (seconds = video [1])} / {timedelta (seconds = video [2])})".replace (":", "\u2236")
                status_emoji = ":bilibili:"
            else:
                status_text, status_emoji = get_status ()
            set_status (status_text, status_emoji)
            time.sleep (60)
    except KeyboardInterrupt:
        set_status (orig_text, orig_emoji)
        print ("Exiting")
        raise SystemExit
