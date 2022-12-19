from wechaty import Wechaty

from .plugins import GithubDiscussionSinkPlugin, SlackSinkPlugin
from .utils import prepare_for_configuration


class RoomSyncBot(Wechaty):
    """
    Listen for events via on_message() from the room and send to Slack
    """

    def __init__(self):
        self._config = prepare_for_configuration()
        super().__init__()
        if self._config["enable_slack"]:
            self.use(SlackSinkPlugin())
            print("Slack Sink Plugin Enabled")

        if self._config["enable_github_discussion"]:
            self.use(GithubDiscussionSinkPlugin())
            print("Github Discussion Sink Plugin Enabled")


async def main():
    """
    Main function
    """
    bot = RoomSyncBot()
    await bot.start()
    print("[RoomSyncBot] started.")
