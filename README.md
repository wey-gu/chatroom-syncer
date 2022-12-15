# Chatroom-Syncer

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Chatroom-Syncer is a project to sync IM Chat Room to the public domain like IRC in the old days, so that the information, context and history of communication could be discoverred, learnt from and referenced by others, anyware, anytime.


https://user-images.githubusercontent.com/1651790/207810877-b86943fa-24b3-479c-ac25-d602a6c5d53c.mp4

## Components and Flow

There are two processes in the system:
- Chatroom Syncer, current code base in Python as the WeChaty Client and the bot
- WeChaty Gateway, which leverages the Wechaty with UOS Wechat Client(also named as a puppet) to be called by the Chatroom Syncer due to WebChaty is not a native Python library, and the Wechaty Gateway is a gRPC server to manipulate and watch WeChat the puppet.

Thus, we need to start the WeChaty Gateway before the Chatroom Syncer.

```asciiarm
┌────────────────────────────┐          ┌────────┐
│                            │          │        │
│ Chatroom Syncer            │          │        │
│                            │          │        │
│ WebChaty.onMessage()       ├──────────▶ Slack  │
│                            │          │        │
└──────────────▲─────────────┘          │        │
               │                        └────────┘
             gRPC
               │
┌──────────────▼──────────────┐
│                             │
│  Wechaty Gateway            │
│                             │
│┌────────────────────────┐   │
││ Wechaty UOS puppet     │   │
│└────────────────────────┘   │
└─────────────────────────────┘
```

## Run

Before running, we need follow prerequisites:

- Configure WeChat Group Names and Slack Channel Names in `config.yaml`, they should exist in both WeChat and Slack.
- Configure Slack API Token in `.env`.

### Run with Docker

Run it in background:

```bash
cp config-example.yaml config.yaml
cp env-example .env
docker-compose up -d
```

Check both containers are Up:

```bash
docker-compose ps
```

In case there are any `Exit 0` containers, give another try of starting up:

```bash
docker-compose up -d
```

Scan the QR code with your WeChat App, and you are ready to go!

```bash
docker logs wechat-room-syncer_chatroom-syncer_1 2>/dev/null | grep -v Wechaty
```

Stop it:

```bash
docker-compose down
```

### Run from host

Run Webchaty gateway first:

```bash
export token="iwonttellyou"
docker run -d \
    --name=wechaty-gateway \
    --net=bridge \
    -p 9009:9009 \
    -e WECHATY_PUPPET_SERVICE_TOKEN="$token" \
    -v /wechaty_data:/wechaty/data \
    --restart=unless-stopped weygu/wechaty-gateway:latest
```

Run Chatroom-Syncer:

```bash
python3 -m pip install chatroom-syncer
cp config-example.yaml config.yaml
export SLACK_TOKEN="xoxb-1234567890-1234567890-1234567890-1234567890"
python3 -m chatroom_syncer
```

## Configuration

### WeChat

Copy the config-example.yaml to config.yaml

```bash
cp config-example.yaml config.yaml
```

And fill in the following fields in the table:

| Field | Description |
| ----  | ----------- |
| `group_channel_mapping` | A mapping from WeChat group name to Slack channel name |
| `enable_avatar`         | Whether to enable generate random emoji based avatar   |


## Contribute

### Build from host

```bash
git clone https://github.com/wey-gu/chatroom-syncer && cd chatroom-syncer
# install pdm
curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -
# install chatroom-syncer
pdm install
```

If dependencies are updated, run `pdm sync` to update the lock manifest.

```bash
pdm sync
```

### Build from docker

```bash
docker-compose -f docker-compose.dev.yaml build
docker-compose -f docker-compose.dev.yaml up -d

# get QR code to scan
docker logs wechat-room-syncer_chatroom-syncer_1 2>/dev/null | grep -v Wechaty

# watch logs of the chatroom syncer
docker logs wechat-room-syncer_chatroom-syncer_1 --follow

# stop the chatroom syncer and remove the container
docker-compose -f docker-compose.dev.yaml down
```
