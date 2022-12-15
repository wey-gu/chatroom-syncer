from wechaty import Wechaty, Message, FileBox
from wechaty_puppet import MessageType

from .utils import (
    format_msg_text,
    send_slack_message,
    prepare_for_configuration,
    get_emoji)


class RoomSyncBot(Wechaty):
    """
    Listen for events via on_message() from the room and send to Slack
    """
    def __init__(self):
        self._config = prepare_for_configuration()
        super().__init__()
        self.slack_token = self._config["slack_token"]
        self.group_to_channel = self._config["group_channel_mapping"]
        self.avatar_cache = {}

    async def on_message(self, msg: Message) -> None:
        room = msg.room()
        if room:
            topic = await room.topic()

            if topic in self.group_to_channel:
                if msg.type() == MessageType.MESSAGE_TYPE_TEXT:
                    text = format_msg_text(msg.text())
                    if text:
                        contact = msg.talker()
                        username = contact.name
                        if self._config["enable_avatar"]:
                            if username not in self.avatar_cache:
                                avatar_emoji = get_emoji()
                                self.avatar_cache[username] = avatar_emoji
                            else:
                                avatar_emoji = self.avatar_cache[username]
                        else:
                            avatar_emoji = None
                        await send_slack_message(
                            text=text,
                            channel=self.group_to_channel[topic],
                            username=username,
                            slack_token=self.slack_token,
                            icon_emoji=avatar_emoji)

                if msg.type() == MessageType.MESSAGE_TYPE_IMAGE:
                    # TBD: send image to slack
                    print('Image File Recieved, ignored now')


async def main():
    """
    Main function
    """
    bot = RoomSyncBot()
    await bot.start()
    print('[RoomSyncBot] started.')
