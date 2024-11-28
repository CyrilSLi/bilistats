# bilistats

bilistats is a simple Python script which updates your Slack status when you are currently watching a video on Bilibili.

## Installation

```
pip -r requirements.txt
```

Create a file named `.env` in the project directory and add the following content:

```
SLACK_TOKEN=[Slack user token with status read & write permissions]
BILIBILI_SESSDATA=[Bilibili SESSDATA cookie]
```

See [https://api.slack.com/concepts/token-types](https://api.slack.com/concepts/token-types) and [https://github.com/SocialSisterYi/bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect) for more information on the environment variables.

## Usage

Run the script and keep it running in the background. The script will update your Slack status every 45 to 60 seconds.