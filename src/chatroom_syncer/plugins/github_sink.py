from __future__ import annotations

import aiohttp
import requests
from wechaty import Message, WechatyPlugin
from wechaty_puppet import MessageType

from ..utils import (
    format_msg_text,
    get_current_year,
    get_week_number,
    prepare_for_configuration,
)


class GithubDiscussionSinkPlugin(WechatyPlugin):
    def __init__(self) -> None:
        super().__init__()
        self._config = prepare_for_configuration()
        self.github_token = self._config["github_token"]
        self.client_headers = {
            "Authorization": f"bearer { self.github_token }"
        }
        self.group_to_category = self._config[
            "group_github_discussion_mapping"
        ]
        # self.sinks_map is typed like Dict[str, dict[str, str]]
        self.sinks_map: dict[str, dict[str, str]] = {}
        self.sink_to_discussion_post_cache: dict[str, str] = {}
        self.init_sinks()

    def init_sinks(self) -> None:
        """
        Verify all sinks are ready, and cache their ids.
        """
        # config.yaml
        # ---
        # enable_github_discussion: true
        # group_github_discussion_mapping:
        #     "NebulaGraph 讨论群测试": "wey-gu/chatroom-syncer/WeChat Chat History"
        # Get github org name, repo name and discussion category names from
        # values of self.group_to_category
        # if error, raise exception

        try:
            for sink in set(self.group_to_category.values()):
                org, repo, category = sink.split("/")
                repo_id, category_id = self.ensure_sink(org, repo, category)
                self.sinks_map[sink] = {
                    "org": org,
                    "repo_name": repo,
                    "category_name": category,
                    "repo_id": repo_id,
                    "category_id": category_id,
                }

        except ValueError:
            raise ValueError(
                "group_github_discussion_mapping should be "
                "in format of org/repo/category_name"
            )

    def ensure_sink(self, org, repo, category) -> tuple[str, str]:
        """
        Verify a github sink is ready, return repo_id and category_id
        """
        with requests.Session() as session:
            headers = self.client_headers
            query = """
                query {
                    repository(owner: "%s", name: "%s") {
                        id
                        discussionCategories(first: 100) {
                            nodes {
                                id
                                name
                            }
                        }
                    }
                }
                """ % (
                org,
                repo,
            )
            with session.post(
                "https://api.github.com/graphql",
                json={"query": query},
                headers=headers,
            ) as resp:
                data = resp.json()
                try:
                    repositoryId = data["data"]["repository"]["id"]
                    # categoryId where its name is category
                    categoryId = [
                        node["id"]
                        for node in data["data"]["repository"][
                            "discussionCategories"
                        ]["nodes"]
                        if node["name"] == category
                    ]
                except Exception as e:
                    raise ValueError(
                        "Getting repositoryId and categoryId failed: %s" % e
                    )
            if categoryId:
                return repositoryId, categoryId[0]
            else:
                raise ValueError(
                    "Category %s not found in %s/%s" % (category, org, repo)
                )

    async def ensure_discussion_post(
        self, title: str, category_id: str, org: str, repo: str, repo_id: str
    ) -> str:
        """
        Ensure a discussion post is ready:
        try get discussion post id, if not found, create it
        return discussion_post_id
        """
        async with aiohttp.ClientSession() as session:
            # first, check if the discussion post exists
            query = """
                query {
                    repository(owner: "%s", name: "%s") {
                        discussions(first: 3, orderBy:
                            {field: CREATED_AT, direction: DESC},
                            categoryId: "%s") {
                            nodes {
                                id
                                title
                            }
                        }
                    }
                }
                """ % (
                org,
                repo,
                category_id,
            )
            async with session.post(
                "https://api.github.com/graphql",
                json={"query": query},
                headers=self.client_headers,
            ) as resp:
                data = await resp.json()
                try:
                    discussion_post_id = [
                        node["id"]
                        for node in data["data"]["repository"]["discussions"][
                            "nodes"
                        ]
                        if node["title"] == title
                    ]
                except Exception as e:
                    raise ValueError(
                        "Getting discussion_post_id failed: %s" % e
                    )
            if discussion_post_id:
                return discussion_post_id[0]
            # if the discussion post does not exist, create it
            # TODO: support config of archive topic body(branding)
            async with session.post(
                "https://api.github.com/graphql",
                json={
                    "query": """
                        mutation {
                            createDiscussion(input: {
                                    repositoryId: "%s",
                                    categoryId: "%s",
                                    title: "%s",
                                    body: "%s"}) {
                                discussion {
                                    id
                                }
                            }
                        }
                        """
                    % (
                        repo_id,
                        category_id,
                        title,
                        f"Archive of WeChat Group: **{title}**",
                    )
                },
                headers=self.client_headers,
            ) as resp:
                data = await resp.json()
                try:
                    return data["data"]["createDiscussion"]["discussion"]["id"]
                except Exception as e:
                    raise ValueError(
                        "Creating discussion_post_id failed: %s" % e
                    )

    async def on_message(self, msg: Message) -> None:
        if not self._config["enable_github_discussion"]:
            # warning: we shouldn't reach here
            print("Github Discussion Sink Plugin Disabled")
            return
        room = msg.room()
        if room:
            topic = await room.topic()

            if topic in self.group_to_category:
                if msg.type() == MessageType.MESSAGE_TYPE_TEXT:
                    # TODO: need to introduce mechanism to avoid format
                    # again in second plugin
                    text = format_msg_text(msg.text())
                    if text:
                        contact = msg.talker()
                        username = contact.name
                        comment_body = f"> {username} said:\n\n{text}"
                        await self.send_github_discussion_message(
                            comment_body=comment_body,
                            room_name=topic,
                            discussion_category=self.group_to_category[topic],
                        )

                if msg.type() == MessageType.MESSAGE_TYPE_IMAGE:
                    # TODO: send image to slack
                    print("Image File Recieved, ignored now")

    async def send_github_discussion_message(
        self, comment_body: str, room_name: str, discussion_category: str
    ) -> str:
        """Send message to Github Discussion"""
        discussion_topic = (
            f"{room_name}-{get_current_year()}-W{get_week_number()}"
        )
        discussion_category_id = self.sinks_map[discussion_category][
            "category_id"
        ]
        if self.sink_to_discussion_post_cache.get(discussion_topic):
            discussion_post_id = self.sink_to_discussion_post_cache[
                discussion_topic
            ]
        else:
            discussion_post_id = await self.ensure_discussion_post(
                discussion_topic,
                discussion_category_id,
                self.sinks_map[discussion_category]["org"],
                self.sinks_map[discussion_category]["repo_name"],
                self.sinks_map[discussion_category]["repo_id"],
            )
            self.sink_to_discussion_post_cache[
                discussion_topic
            ] = discussion_post_id
        async with aiohttp.ClientSession() as session:
            headers = self.client_headers
            query = """
                mutation {
                    addDiscussionComment(
                        input: {discussionId: "%s", body: "%s"}) {
                        comment {
                            id
                        }
                    }
                }
                """ % (
                discussion_post_id,
                comment_body,
            )
            async with session.post(
                "https://api.github.com/graphql",
                json={"query": query},
                headers=headers,
            ) as resp:
                data = await resp.json()
                try:
                    discussionCommentId = data["data"]["addDiscussionComment"][
                        "comment"
                    ]["id"]
                except Exception as e:
                    raise ValueError(
                        "Creating discussionCommentId failed: %s" % e
                    )
            return discussionCommentId
