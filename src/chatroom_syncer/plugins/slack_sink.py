from __future__ import annotations

import hashlib
import math

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient
from wechaty import Message, WechatyPlugin
from wechaty_puppet import MessageType

from ..emoji import emoji_list
from ..utils import format_msg_text, prepare_for_configuration

HASH_BYTES = math.ceil(math.log(len(emoji_list), 2) / 8)


class SlackSinkPlugin(WechatyPlugin):
    def __init__(self):
        super().__init__()
        self._config = prepare_for_configuration()
        if self._config["enable_slack"]:
            self.slack_token = self._config["slack_token"]
            self.group_to_channel = self._config["group_channel_mapping"]

    async def on_message(self, msg: Message) -> None:
        if not self._config["enable_slack"]:
            # warning: we shouldn't reach here
            print("Slack Sink Plugin Disabled")
            return
        room = msg.room()
        if room:
            topic = await room.topic()

            if topic in self.group_to_channel:
                if msg.type() == MessageType.MESSAGE_TYPE_TEXT:
                    # TODO: need to introduce mechanism to avoid format
                    # again in second plugin
                    text = format_msg_text(msg.text())
                    if text:
                        msg.text()
                        contact = msg.talker()
                        username = contact.name
                        if self._config["enable_avatar"]:
                            avatar_emoji = self.get_emoji(username)
                        else:
                            avatar_emoji = None
                        await self.send_slack_message(
                            text=text,
                            channel=self.group_to_channel[topic],
                            username=username,
                            slack_token=self.slack_token,
                            icon_emoji=avatar_emoji,
                        )

                if msg.type() == MessageType.MESSAGE_TYPE_IMAGE:
                    # TBD: send image to slack
                    print("Image File Recieved, ignored now")

    @staticmethod
    def get_emoji(username: str) -> str:
        """Get emoji"""
        username_hash = hashlib.sha256(username.encode("utf-8")).digest()
        # Get the first 2 bytes of the sha256 digest, that is max 65535
        # then get the index by mod the length of emoji list
        emoji_index = int.from_bytes(username_hash[:HASH_BYTES], "big")
        return emoji_list[emoji_index % len(emoji_list)]

    @staticmethod
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
