import os

from requests.api import get, request
from slack_bolt import App
from slack_sdk.errors import SlackApiError

import logging

import requests
import json
import time
import datetime
import threading
import os
import random

import quickstart

logging.basicConfig(level=logging.INFO)


# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


@app.action("actionId-0")
def handle_some_action(ack, body, logger, client, say):
    """
        Triggered when a user clicks the button to accept the activity
    """
    ack()
    logger.info(body)

    channel_id = body["container"]["channel_id"]
    message_ts = body["container"]["message_ts"]

    say("accepted")

    # getting user selected time
    timepickers = body["state"]["values"]
    timepickers_list = list(timepickers.items())
    initial_time = timepickers_list[0][1]["timepicker-action"]["selected_time"]
    end_time = timepickers_list[1][1]["timepicker-action"]["selected_time"]

    # call some functions to add to calendar

    app.client.chat_delete(
        channel=channel_id,
        ts=message_ts
    )


@app.action("actionId-1")
def handle_some_action(ack, body, logger, client, say):
    ack()
    logger.info(body)
    channel_id = body["container"]["channel_id"]
    message_ts = body["container"]["message_ts"]

    say("Invite declined, see you soon! \n If you wish to unsubscribe visit <link>")
    
    app.client.chat_delete(
        channel=channel_id,
        ts=message_ts
    )


# removed for now
"""
@app.action("actionId-2")
def handle_some_action(ack, body, logger, client, say):
    #UNFINISHED (Not sure if doable)
    ack()
    logger.debug(body)
    #user_id = body["user_id"]

    say("Different activity")


    #client.chat_postMessage(
    #    channel=user_id, 
    #    as_user=True, 
    #    text="Accepted!"
    #)
"""

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
    logging.debug(user_info)

    for user in user_info:
        send_user_invite(user)

def send_user_invite(user):
    name = user["name"]
    slack_id = user["slack_id"]
    activites = user["activities"]

    logging.info(f"Sending user invite to {name}, slack id = {slack_id}")

    if not activites:
        app.client.chat_postMessage(
        as_user=True, 
        channel=slack_id, 
        text=f"It appears you have no activites set yet {name}! Please go to <link> to set them up"
    )
    else:
        invite = create_invite(name, activites)

        app.client.chat_postMessage(
            as_user=True, 
            channel=slack_id, 
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

    logging.debug(invite)  
    return invite


def get_user_time():

    start_time = "12:00"
    finish_time = "14:50"

    logging.info("Calling Google API main func")
    #start_time, finish_time = quickstart.main()

    return start_time, finish_time


def get_user_activity(activities):
    """ DONE 
        Chooses an activity to send to the user based on their chosen activies. 
        The choice is then chosen randomly with weights determined by their likeScale
    """

    weights = []
    activity_names = []
    for activity in activities:
        logging.debug(activity)
        weights.append(activity["likeScale"])
        activity_names.append(activity["name"])


    # Making weighted choise of activity based on likeScale
    logging.debug(activity_names)
    logging.debug(weights)
    choice = random.choices(population=activity_names, weights=weights, k=1)[0]

    return choice


def get_users_info():
    """
    Returns a dict of user id, name, email and the activities they like to do
    """
    
    # requesting API for user information
    users_request = requests.request("GET", "https://rrmadhacks-oraseemeaukinnovation.builder.ocp.oraclecloud.com/ic/builder/rt/Calendar_Break_Insertion_Tool/live/resources/data/Account").json()
    user_activities = requests.request("GET", "https://rrmadhacks-oraseemeaukinnovation.builder.ocp.oraclecloud.com/ic/builder/rt/Calendar_Break_Insertion_Tool/live/resources/data/UserActivities").json()
    activities_list = requests.request("GET", "https://rrmadhacks-oraseemeaukinnovation.builder.ocp.oraclecloud.com/ic/builder/rt/Calendar_Break_Insertion_Tool/live/resources/data/Activities").json()
    
    users_info = []

    try:
        # Call the users.list method using the WebClient
        result = app.client.users_list()

    except SlackApiError as e:
        logging.error("Error creating conversation: {}".format(e))

    for user in users_request["items"]:
        id = user["id"]
        name = user["name"]
        email = user["email"]
        activities = []

        slack_id = ""

        # getting users slack id by comparing emails
        for user in result["members"]:
            logging.debug(user["profile"])
            try:
                if user["profile"]["email"] == email:
                    slack_id = user["id"]
                    break
            except KeyError as e:
                logging.info("No email found for {}".format(user["profile"]["real_name"]))
                continue

        if slack_id == "":
            logging.info(f"Slack ID not found for {name}, continuing")
            continue
        else:
            logging.info(f"Sladk ID {slack_id} found for {name}")

        # gathering user information together 
        for user_activity in user_activities["items"]:
            if user_activity["account"] == id:
                for activity in activities_list["items"]:
                    if activity["id"] == user_activity["activity"]:
                        activities.append({"name": activity["name"], "desc": activity["description"], "likeScale": user_activity["likeScale"]})


        # adding all user info into a dictionary
        users_info.append({"id" : id, "name": name, "email": email, "slack_id": slack_id, "activities": activities})
        logging.debug(users_info)

    return users_info
            

# Start your app
if __name__ == "__main__":

    # creating the daily message sending thread
    try:
        logging.info("Creating thread")
        time_keeper = threading.Thread(target=daily_checker)
        time_keeper.start()
        logging.info("Thread created successfully")
    except Exception as e:
        logging.error("Thread creation failed: " + str(e))

    logging.info("Running main app thread")
    app.start(port=int(os.environ.get("PORT", 3000)))