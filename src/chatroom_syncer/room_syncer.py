from wechaty import Wechaty, Message, FileBox
from wechaty_puppet import MessageType


from .utils import format_msg_text, send_slack_message, prepare_for_configuration


class RoomSyncBot(Wechaty):
    """
    Listen for events via on_message() from the room and send to Slack
    """
    def __init__(self):
        self._config = prepare_for_configuration()
        super().__init__()
        self.slack_token = self._config["slack_token"]
        self.group_to_channel = self._config["group_channel_mapping"]

    async def on_message(self, msg: Message) -> None:
        room = msg.room()
        if room:
            topic = await room.topic()

            if topic in self.group_to_channel:
                if msg.type() == MessageType.MESSAGE_TYPE_TEXT:
                    text = format_msg_text(msg.text())
                    if text:
                        username = msg.talker().name
                        # TBD: get avatar from wechaty and cache it
                        await send_slack_message(
                            text=text,
                            channel=self.group_to_channel[topic],
                            username=username,
                            slack_token=self.slack_token)

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
