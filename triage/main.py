import os
import logging
from slack_bolt import App

logging.basicConfig(level=logging.DEBUG)

# process_before_response must be True when running on FaaS
app = App(process_before_response=True)

# This appears to be a slash command
@app.command("/triage")
def hello_command(ack):
    ack("Hi from The Jira and Slack Integration bot! When you are ready, just send me a DM in a thread and I will help you create a Jira ticket.")

# Flask adapter
from slack_bolt.adapter.google_cloud_functions import SlackRequestHandler
from flask import Request


handler = SlackRequestHandler(app)

# This appears to be the mention event
@app.event("app_mention")
def event_test(body, say, logger):
    logger.info(body)
    # Check if this mention is in a thread
    if "thread_ts" in body["event"]:
    #   # Grab the parent message
    #   parent_message = app.client.conversations_replies(
    #     channel=body["event"]["channel"],
    #     ts=body["event"]["thread_ts"]
    #   )
    #   # Tell them the parent message
    #   say(f"Your parent message was: {parent_message['messages'][0]['text']}", thread_ts=body["event"]["ts"])
      say("Creating your ticket!", thread_ts=body["event"]["ts"])
    else:
      say("Sadly, I can only create tickets in a thread. Please send me a DM in a thread.")




def triage(req: Request):
  """HTTP Cloud Function.
    Args:
        req (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
  app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
  )
  return handler.handle(req)