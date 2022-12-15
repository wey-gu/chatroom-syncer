# Utils
import os, yaml, random

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from .emoji import emoji_list


def format_msg_text(text: str) -> str:
    """Format text to be sent"""
    text = text.replace("<br/>", "\n")
    return text


def prepare_for_wechaty() -> None:
    """Prepare for wechaty envrioment variables"""
    # check envriotment variable, if not set, set it to default value
    if not os.environ.get("WECHATY_PUPPET_SERVICE_ENDPOINT"):
        os.environ["WECHATY_PUPPET_SERVICE_ENDPOINT"] = "127.0.0.1:9009"
    if not os.environ.get("WECHATY_PUPPET_SERVICE_TOKEN"):
        os.environ["WECHATY_PUPPET_SERVICE_TOKEN"] ="foobar2000"
    os.environ["WECHATY_PUPPET_WECHAT_PUPPETEER_UOS"] = "true"


def prepare_for_slack() -> str:
    """Prepare for slack"""
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    if not slack_token:
        print("No slack token found in environment variable: SLACK_BOT_TOKEN")
        exit(1)
    return slack_token


def prepare_for_configuration() -> dict:
    """Prepare for room syncer"""
    prepare_for_wechaty()
    slack_token = prepare_for_slack()

    config_file = os.environ.get("ROOM_SYNCER_CONFIG", "config.yaml")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    assert validate_config(config)
    config["slack_token"] = slack_token
    return config


def validate_config(config: dict) -> bool:
    """Validate config file"""
    if not config.get("group_channel_mapping"):
        print("No group_channel_mapping found in config file")
        return False
    return True


def get_emoji() -> str:
    """Get emoji"""
    return random.choice(emoji_list)


async def send_slack_message(
        text: str, channel: str, username: str, slack_token: str,
        icon_emoji: [str, None] = None) -> None:
    """Send message to Slack"""
    client = AsyncWebClient(token=slack_token)
    try:
        response = await client.chat_postMessage(
            channel=channel,
            text=text,
            username=username,
            icon_emoji=icon_emoji
        )
        print(response)
    except SlackApiError as e:
        print("Error sending message: {}".format(e))
