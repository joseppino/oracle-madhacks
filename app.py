import os
from slack_bolt import App

import logging


logging.basicConfig(level=logging.DEBUG)

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

@app.message("Hello World")
def hello_world(ack, client, logger, body):
    """ Sends user a DM with text 'Hello World!' """
    ack()
    logger.info(body)
    user_id = body["user_id"]
    channel_id = body["channel_id"]

    client.chat_postMessage(
        channel=channel_id,
        as_user=True,
        text="Hello world!")

@app.command("/help")
def help(ack, logger, body, client):
    """ Lists all currently active commands """
    ack()
    logger.info(body)
    user_id = body["user_id"]


    client.chat_postMessage(
        channel=user_id,
        as_user=True,
        text="I am here to help you"
    )

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))