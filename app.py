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
    #channel_id = body["channel_id"]

    client.chat_postMessage(
        channel=user_id,
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

@app.command("/add_event")
def add_event(ack, logger, body, client):
    """ Suggests a new event """
    ack()
    logger.info(body)
    user_id = body["user_id"]

    client.chat_postMessage(
        channel=user_id, 
        as_user=True, 
	blocks = [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "Hello! There is a gap in your calendar at *13:00*, perhaps you would like *to go on a walk*"
			}
		},
		{
			"type": "input",
			"element": {
				"type": "timepicker",
				"initial_time": "13:00",
				"placeholder": {
					"type": "plain_text",
					"text": "Select time",
					"emoji": True
				},
				"action_id": "timepicker-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Start time",
				"emoji": True
			}
		},
		{
			"type": "input",
			"element": {
				"type": "timepicker",
				"initial_time": "13:30",
				"placeholder": {
					"type": "plain_text",
					"text": "Select time",
					"emoji": True
				},
				"action_id": "timepicker-action"
			},
			"label": {
				"type": "plain_text",
				"text": "Finish time",
				"emoji": True
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Accept",
						"emoji": True
					},
					"value": "click_me_123",
					"action_id": "actionId-0",
					"style": "primary"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Decline",
						"emoji": True
					},
					"value": "Decline",
					"action_id": "actionId-1",
					"style": "danger"
				},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Different activity!",
						"emoji": True
					},
					"value": "Decline",
					"action_id": "actionId-2"
				}
			]
		}
	]
    )

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))