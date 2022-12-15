# Chatroom-Syncer

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Chatroom-Syncer is a project to sync IM Chat Room to the public domain like IRC in the old days, so that the information, context and history of communication could be discoverred, learnt from and referenced by others, anyware, anytime.

## Run

### Run with Docker

Run it in background:

```bash
cp config-example.yaml config.yaml
cp env-example .env
docker-compose up -d
```

Scan the QR code with your WeChat App, and you are ready to go!

```bash
docker logs wechat-room-syncer_chatroom-syncer_1 2>/dev/null | grep -v Wechaty
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
```
