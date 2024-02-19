import os
import logging
from slack_bolt import App

logging.basicConfig(level=logging.DEBUG)

# process_before_response must be True when running on FaaS
app = App(process_before_response=True)

# This appears to be a slash command
@app.command("/triage")
def hello_command(ack, logger):
  logger.info("I see a slash command!")
  ack("Hi from The Jira and Slack Integration bot! When you are ready, just send me a DM in a thread and I will help you create a Jira ticket.")

# Flask adapter
from slack_bolt.adapter.google_cloud_functions import SlackRequestHandler
from flask import Request


handler = SlackRequestHandler(app)

# This appears to be the mention event
@app.event("app_mention")
def event_test(body, say, logger):
  logger.info("I see a mention!")
  logger.info(body)
  # Check if this mention is in a thread
  if "thread_ts" in body["event"]:
    # Find who called the bot
    assignee = body["event"]["user"]

    # Find the original message sender
    reporter = app.client.conversations_replies(
      channel=body["event"]["channel"],
      ts=body["event"]["thread_ts"]
    )["messages"][0]["user"]
    
    description = app.client.conversations_replies(
      channel=body["event"]["channel"],
      ts=body["event"]["thread_ts"]
    )["messages"][0]["text"]
    
    # TODO: Check what other info we can grab from the message
    parent_message_meta = app.client.conversations_replies(
      channel=body["event"]["channel"],
      ts=body["event"]["thread_ts"]
    )["messages"][0]
    
    # Just print the testing message
    say(f"Here is the message: {parent_message_meta}", thread_ts=body["event"]["ts"])

    # Say something like "Creating your ticket assignment to <assignee>!"
    say(f"Creating your ticket <@{assignee}> for reporter <@{reporter}> with description {description}!", thread_ts=body["event"]["ts"])
  else:
    say("Sadly, I can only create tickets in a thread. Please send me a DM in a thread.")

def triage(req: Request):
  app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
  )
  return handler.handle(req)

# Step1: Create a new Slack App: https://api.slack.com/apps
# Bot Token Scopes: app_mentions:read,chat:write,commands

# Step2: Set env variables
# vi .env.yaml

# Step3: Create a new Google Cloud project (if needed)
# gcloud projects create YOUR_PROJECT_NAME
# gcloud config set project YOUR_PROJECT_NAME

# Step4: Deploy a function in the project (see README for more details)
# gcloud functions describe hello_bolt_app

# Step5: Set Request URL
# Set URL in README to the following:
#  * slash command: /triage
#  * Events Subscriptions & add `app_mention` event