FROM python:3.10

# Install chatroom-syncer using pip
RUN pip install chatroom-syncer

# Set the working directory to /app
WORKDIR /app

# Set environment variables for WECHATY_PUPPET_SERVICE_ENDPOINT, WECHATY_PUPPET_SERVICE_TOKEN, and SLACK_BOT_TOKEN
ENV WECHATY_PUPPET_SERVICE_ENDPOINT="127.0.0.1:9009"
ENV WECHATY_PUPPET_SERVICE_TOKEN="test"
ENV SLACK_BOT_TOKEN=""

# Run the chatroom-syncer module when the container is run
CMD ["python3", "-m", "chatroom-syncer"]
