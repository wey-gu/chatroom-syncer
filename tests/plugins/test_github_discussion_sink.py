import pytest

from chatroom_syncer.plugins.github_discussion_sink import GithubDiscussionSinkPlugin


def test_GithubDiscussionSinkPlugin_init_sinks():
    plugin = GithubDiscussionSinkPlugin()
    plugin.init_sinks()
    # print(plugin.sinks_map)

    assert plugin.sinks_map == {
        "wey-gu/chatroom-syncer/WeChat Chat History": {
            "org": "wey-gu",
            "repo_name": "chatroom-syncer",
            "category_name": "WeChat Chat History",
            "repo_id": "R_kgDOInpBGg",
            "category_id": "DIC_kwDOInpBGs4CTITf",
        }
    }


def test_GithubDiscussionSinkPlugin_ensure_sink():
    plugin = GithubDiscussionSinkPlugin()
    repo_id, category_id = plugin.ensure_sink(
        "wey-gu", "chatroom-syncer", "WeChat Chat History"
    )
    # print(repo_id, category_id)

    assert repo_id == "R_kgDOInpBGg"
    assert category_id == "DIC_kwDOInpBGs4CTITf"


def test_GithubDiscussionSinkPlugin_ensure_sink_not_found():
    plugin = GithubDiscussionSinkPlugin()
    with pytest.raises(ValueError):
        plugin.ensure_sink("wey-gu", "chatroom-syncer", "not-found-category")


@pytest.mark.asyncio
async def test_GithubDiscussionSinkPlugin_ensure_discussion_post():
    plugin = GithubDiscussionSinkPlugin()
    plugin.init_sinks()
    chatroom_post_title = "My_Room_Group-2022-W50"
    category_id = plugin.sinks_map[
        "wey-gu/chatroom-syncer/WeChat Chat History"
    ]["category_id"]
    org = plugin.sinks_map["wey-gu/chatroom-syncer/WeChat Chat History"]["org"]
    repo_name = plugin.sinks_map["wey-gu/chatroom-syncer/WeChat Chat History"][
        "repo_name"
    ]
    repo_id = plugin.sinks_map["wey-gu/chatroom-syncer/WeChat Chat History"][
        "repo_id"
    ]
    discussion_post_id = await plugin.ensure_discussion_post(
        chatroom_post_title, category_id, org, repo_name, repo_id
    )

    assert discussion_post_id is not None


@pytest.mark.asyncio
async def test_GithubDiscussionSinkPlugin_send_github_discussion_message():
    plugin = GithubDiscussionSinkPlugin()
    plugin.init_sinks()

    comment_body = "test comment"
    room_name = "bot-test"
    discussion_category = plugin.group_to_category[room_name]
    # print(f"discussion_category: {discussion_category}")
    comment_id = await plugin.send_github_discussion_message(
        comment_body, room_name, discussion_category
    )
    # print(f"comment_id: {comment_id}")
    assert comment_id is not None


# export github_token=xxx
# pip install pytest-asyncio
# pytest tests/plugins/test_github_discussion_sink.py

# Note, this is kinda end to end test, so it will create a
# discussion post and a comment in the discussion post
