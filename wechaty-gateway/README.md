## Run it

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
