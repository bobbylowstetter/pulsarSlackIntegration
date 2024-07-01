#region Imports and Setup
import os
import logging
from slack_bolt import App

# Jira API stuff for Future Features
import http.client
import json

# Flask adapter
from slack_bolt.adapter.google_cloud_functions import SlackRequestHandler
from flask import Request

logging.basicConfig(level=logging.DEBUG)

# process_before_response must be True when running on FaaS
app = App(process_before_response=True)

handler = SlackRequestHandler(app)
#endregion

#region Shared Variables
# ServiceNow API stuff

# Jira API stuff for Future Features
jira_authorization=os.environ.get("JIRA_AUTH")
#endregion

#region Slash Command (/triage) Functionality
# This is the slash command. We are not really using it, but it will notify them on how to use the bot.
@app.command("/triage")
def hello_command(ack, logger):
  logger.info("I see a slash command!")
  ack("Hi from The Pulsar Slack Integration bot! Use reactions to have me create (:eyes) or complete (:white_check_mark) a ticket.")
#endregion

# TODO: Handle if a reaction is removed (Future Feature)

#region Reaction_Added Event Functionality
@app.event("reaction_added")
def handle_reaction_added(body, say, logger):
  #region Get variables from Slack
  assignee = body["event"]["user"]
  assignee_email = app.client.users_info(
      user=assignee
  )["user"]["profile"]["email"]
  
  reaction = body["event"]["reaction"]
  channel = body["event"]["item"]["channel"]
  ts = body["event"]["item"]["ts"]
  # Convert ts to the URL
  url = f"https://banno.slack.com/archives/{channel}/p{ts.replace('.', '')}"
  
  reporter = app.client.conversations_replies(
    channel=channel,
    ts=ts
  )["messages"][0]["user"]
  reporter_email = app.client.users_info(
      user=reporter
  )["user"]["profile"]["email"]
  
  description = app.client.conversations_replies(
    channel=channel,
    ts=ts
  )["messages"][0]["text"]
  #endregion
  
  # TODO: Don't allow this to be run from within a thread (Future Feature)
  
  #region :jh: Reaction Functionality (Create a ticket)
  if reaction == "jh":
    
    # TODO: Create a function to create a ticket (Needed Feature)
    say(f"Creating a ticket for {assignee_email}...")
    #endregion
  
  #region :white_check_mark: Reaction Functionality (Complete a ticket)
  # TODO: Create a function to complete a ticket (Future Feature)
  #endregion

#endregion

#region App_Mention (@Pulsar Slack Integration) Event Functionality
@app.event("app_mention")
def event_test(say, logger):
  logger.info("I see a mention!")
  say("Hi there! I am The Pulsar Slack Integration bot! Use reactions to have me create (:jh) a ticket.")

def triage(req: Request):
  app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
  )
  return handler.handle(req)
#endregion

#region ServiceNow API Functions

# TODO: Create a function to create a ticket (Needed Feature)
# TODO: Create a function to complete a ticket (Future Feature)

#endregion