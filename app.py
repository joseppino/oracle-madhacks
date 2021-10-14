import os
import json
from slack_bolt import App

import logging


logging.basicConfig(level=logging.DEBUG)

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

@app.message("Hello World")
def secure_cloud_message(ack, client, logger, body):
    """ Responds to user when exact phrase is detected """
    ack()
    logger.info(body)
    user_id = body["user_id"]

    client.chat_postMessage(
        channel=user_id,
        as_user=True,
        text="Hello world!")


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))