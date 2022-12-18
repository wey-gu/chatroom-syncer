# Utils
from __future__ import annotations

import datetime
import os
import re
from typing import TypedDict

import yaml
from dotenv import load_dotenv


class Config(TypedDict):
    """Config, see config-example.yaml"""

    # slack channel as target
    enable_slack: bool
    group_channel_mapping: dict[str, str]
    slack_token: str
    enable_avatar: bool
    # github discussion as target
    enable_github_discussion: bool
    group_discussion_mapping: dict[str, str]


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
    try:
        slack_token = os.environ["SLACK_BOT_TOKEN"]
    except KeyError:
        load_dotenv()
        slack_token = os.environ["SLACK_BOT_TOKEN"]
    if not slack_token:
        raise RuntimeError(
            "No slack token found in environment variable: SLACK_BOT_TOKEN"
        )
    return slack_token


def prepare_for_github() -> str:
    """Prepare for github"""
    try:
        github_token = os.environ.get("GITHUB_TOKEN")
    except KeyError:
        load_dotenv()
        github_token = os.environ.get("GITHUB_TOKEN", None)

    if not github_token:
        raise RuntimeError(
            "No github credential found in environment variable: "
            "GITHUB_TOKEN"
        )
    return github_token


def prepare_for_configuration() -> Config:
    """Prepare for room syncer"""
    prepare_for_wechaty()

    config_file = os.environ.get("ROOM_SYNCER_CONFIG", "config.yaml")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    # prepare for credentials of sync targets

    if config["enable_slack"]:
        config["slack_token"] = prepare_for_slack()
    if config["enable_github_discussion"]:
        config["github_token"] = prepare_for_github()

    validate_config(config)

    return config


def validate_config(config: Config) -> None:
    """Validate config file"""
    if config["enable_slack"]:
        if not config.get("group_channel_mapping"):
            raise ValueError("No group_channel_mapping found in config file")
    if config["enable_github_discussion"]:
        if not config.get("group_github_discussion_mapping"):
            raise ValueError(
                "No group_github_discussion_mapping found in config file"
            )


def get_current_year() -> int:
    """Get current year"""
    return datetime.datetime.now().year


def get_week_number() -> int:
    """Get week number"""
    return datetime.datetime.now().isocalendar()[1]
