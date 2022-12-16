# Utils
from __future__ import annotations

import hashlib
import math
import os
import re
from typing import TypedDict

import yaml
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from .emoji import emoji_list

HASH_BYTES = math.ceil(math.log(len(emoji_list), 2) / 8)


class Config(TypedDict):
    """Config"""

    group_channel_mapping: dict[str, str]
    slack_token: str
    enable_avatar: bool


def format_msg_text(text: str) -> str:
    """Format text to be sent"""
    # render newline correctly
    text = text.replace("<br/>", "\n")
    # remove URL trackers
    patter = re.compile(r"<a\s+[^>]*>(.*?)</a>")
    text = patter.sub(r"\1", text)
    # remove emoji in picture <img> tag
    patter = re.compile(r"<img[^>]*>")
    text = patter.sub(r"", text)
    return text


def prepare_for_wechaty() -> None:
    """Prepare for wechaty envrioment variables"""
    # check envriotment variable, if not set, set it to default value
    if not os.environ.get("WECHATY_PUPPET_SERVICE_ENDPOINT"):
        os.environ["WECHATY_PUPPET_SERVICE_ENDPOINT"] = "127.0.0.1:9009"
    if not os.environ.get("WECHATY_PUPPET_SERVICE_TOKEN"):
        os.environ["WECHATY_PUPPET_SERVICE_TOKEN"] = "foobar2000"
    os.environ["WECHATY_PUPPET_WECHAT_PUPPETEER_UOS"] = "true"


def prepare_for_slack() -> str:
    """Prepare for slack"""
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    if not slack_token:
        raise RuntimeError(
            "No slack token found in environment variable: SLACK_BOT_TOKEN"
        )
    return slack_token


def prepare_for_configuration() -> Config:
    """Prepare for room syncer"""
    prepare_for_wechaty()
    slack_token = prepare_for_slack()

    config_file = os.environ.get("ROOM_SYNCER_CONFIG", "config.yaml")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    validate_config(config)
    config["slack_token"] = slack_token
    return config


def validate_config(config: Config) -> None:
    """Validate config file"""
    if not config.get("group_channel_mapping"):
        raise ValueError("No group_channel_mapping found in config file")


def get_emoji(username: str) -> str:
    """Get emoji"""
    username_hash = hashlib.sha256(username.encode("utf-8")).digest()
    # Get the first 2 bytes of the sha256 digest, that is max 65535
    # then get the index by mod the length of emoji list
    emoji_index = int.from_bytes(username_hash[:HASH_BYTES], "big")
    return emoji_list[emoji_index % len(emoji_list)]


async def send_slack_message(
    text: str,
    channel: str,
    username: str,
    slack_token: str,
    icon_emoji: str | None = None,
) -> None:
    """Send message to Slack"""
    client = AsyncWebClient(token=slack_token)
    try:
        response = await client.chat_postMessage(
            channel=channel,
            text=text,
            username=username,
            icon_emoji=icon_emoji,
        )
        print(response)
    except SlackApiError as e:
        print("Error sending message: {}".format(e))
