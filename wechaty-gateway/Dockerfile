FROM node:lts-slim

# thanks to https://github.com/longjunyu2/WechatyDocker/blob/main/Dockerfile
ENV TIMEZONE=Asia/Shanghai \
    WECHATY_PUPPET_WECHAT_PUPPETEER_UOS=true \
    WECHATY_PUPPET_SERVICE_TOKEN="foobar2000" \
    WECHATY_PUPPET="wechaty-puppet-wechat" \
    WECHATY_LOG="verbose" \
    WECHATY_PUPPET_SERVER_PORT="9009" \
    WECHATY_PUPPET_SERVICE_NO_TLS_INSECURE_SERVER=true \
    PUID=0 \
    GUID=0

RUN apt update \
    && apt dist-upgrade -y \
    && apt install -y libglib2.0-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2  libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

VOLUME [ "/wechaty_data" ]
WORKDIR /wechaty_data
COPY package.json package-lock.json ./
RUN npm install

EXPOSE 9009/tcp

CMD npm start -- --token $WECHATY_PUPPET_SERVICE_TOKEN --port $WECHATY_PUPPET_SERVER_PORT --puppet $WECHATY_PUPPET
