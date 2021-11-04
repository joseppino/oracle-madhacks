import os

from requests.api import get, request
from slack_bolt import App

import logging

import requests
import json
import time
import datetime
import threading
import os
import random

import quickstart

logging.basicConfig(level=logging.DEBUG)


# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

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
    

    

@app.action("actionId-0")
def handle_some_action(ack, body, logger, client, say):
    """
        Triggered when a user clicks the button to accept the activity
    """
    ack()
    logger.info(body)

    say("accepted")
    #say(body["message"]["blocks"][1]["element"])

    timepickers = body["state"]["values"]

    timepickers_list = list(timepickers.items())

    logger.info(timepickers_list)

    initial_time = timepickers_list[0][1]["timepicker-action"]["selected_time"]
    logger.info(initial_time)
    end_time = timepickers_list[1][1]["timepicker-action"]["selected_time"]
    logger.info(end_time)

    say(initial_time)
    say(end_time)

    # make api calls to add to calender here


    #response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.text)

    #user_id = body["user_id"]

    #client.chat_postMessage(
    #    channel=user_id, 
    #    as_user=True, 
    #    text="Accepted!"
    #)

@app.action("actionId-1")
def handle_some_action(ack, body, logger, client, say):
    ack()
    logger.info(body)
    #user_id = body["user_id"]

    say("Declined")
    

    #client.chat_postMessage(
    #    as_user=True, 
    #    channel=user_id, 
    #    text="Accepted!"
    #)


# this func may be unecessary
@app.action("actionId-2")
def handle_some_action(ack, body, logger, client, say):
    ack()
    logger.info(body)
    #user_id = body["user_id"]

    say("Different activity")


    #client.chat_postMessage(
    #    channel=user_id, 
    #    as_user=True, 
    #    text="Accepted!"
    #)


def daily_checker():
    # here for debugging
    send_all_invites()


    while True:

        # setting timers and sleeping thread
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        scheduled_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        scheduled_timestamp = scheduled_time.strftime('%s')
        logging.info("Thread sleeping till " + scheduled_timestamp)
        time_to_sleep = int(scheduled_timestamp) - time.time()
        logging.info("Thread sleeping for " + str(time_to_sleep))
        time.sleep(time_to_sleep)

        # after thread wakes up at 9am (?)
        logging.info("Thread waking up at: " + datetime.datetime.now())

        logging.info("Thread doing daily message sending")

        try:
            # sending all users daily invites
            send_all_invites()
            logging.info("Thread completed daily message sending")
        except:
            logging.error("Thread failed daily message sending")

    
def send_all_invites():
    user_info = get_users_info()

    for user in user_info:
        send_user_invite(user)

def send_user_invite(user):
    name = user["name"]
    email = user["email"]
    slack = user["slack"]
    activites = user["activities"]

    invite = create_invite(name, activites)


    app.client.chat_postMessage(
        as_user=True, 
        channel="U02H9TLBM7G", 
        blocks=invite,
        text="Hello from the Automatic Calendar Break Insertion Tool!"
    )

def create_invite(name, activities):
    """ Populates invite template with variables which is sent as a Slack Block to the user """

    start_time, finish_time = get_user_time()

    chosen_activity = get_user_activity(activities)
    logging.info("Chosen activity is: " + chosen_activity)


    # populating the invite with variables
    invite = [  
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Hello {name}! There is a gap in your calendar at {start_time}, perhaps you would like {chosen_activity}"
        }
    },
    {
        "type": "input",
        "element": {
            "type": "timepicker",
            "initial_time": f"{start_time}",
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
            "initial_time": f"{finish_time}",
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
                "action_id": "actionId-2"}
            ]
        }
    ]

    logging.info(invite)  
    return invite


def get_user_time():
    # calendar API calls here
    start_time = "12:00"
    finish_time = "13:00"

    logging.info("Calling quickstart main func")
    quickstart.main()

    return start_time, finish_time


def get_user_activity(activities):
    # do some random choosing of user activities based on like scale

    weights = []
    activity_names = []
    for activity in activities:
        weights.append(activity["likeScale"])
        activity_names.append(activity["name"])


    # Making weighted choise of activity based on likeScale
    logging.info(len(activity_names))
    logging.info(len(weights))
    choice = random.choices(population=activity_names, weights=weights, k=1)[0]

    return choice


def get_users_info():
    """
    Returns a dict of user id, name, email and the activities they like to do
    """
    
    users_request = requests.request("GET", "https://rrmadhacks-oraseemeaukinnovation.builder.ocp.oraclecloud.com/ic/builder/rt/Calendar_Break_Insertion_Tool/live/resources/data/Account").json()
    #logging.info(response.json())

    user_activities = requests.request("GET", "https://rrmadhacks-oraseemeaukinnovation.builder.ocp.oraclecloud.com/ic/builder/rt/Calendar_Break_Insertion_Tool/live/resources/data/UserActivities").json()

    activities_list = requests.request("GET", "https://rrmadhacks-oraseemeaukinnovation.builder.ocp.oraclecloud.com/ic/builder/rt/Calendar_Break_Insertion_Tool/live/resources/data/Activities").json()
    
    users_info = []

    for user in users_request["items"]:
        id = user["id"]
        name = user["name"]
        email = user["email"]
        slack = user["slack"]

        activities = []
        #logging.info(user_activities["items"])

        for user_activity in user_activities["items"]:
            if user_activity["account"] == id:
                for activity in activities_list["items"]:
                    if activity["id"] == user_activity["activity"]:
                        activities.append({"name": activity["name"], "desc": activity["description"], "likeScale": user_activity["likeScale"]})

        # adding all user info into a dictionary
        users_info.append({"id" : id, "name": name, "email": email, "slack": slack, "activities": activities})


    #logging.info(users_info)

    return users_info
            

# Start your app
if __name__ == "__main__":

    try:
        logging.info("Creating thread")
        time_keeper = threading.Thread(target=daily_checker)
        time_keeper.start()
        logging.info("Thread created successfully")
    except Exception as e:
        logging.error("Thread creation failed: " + str(e))

    logging.info("Running main app thread")
    app.start(port=int(os.environ.get("PORT", 3000)))