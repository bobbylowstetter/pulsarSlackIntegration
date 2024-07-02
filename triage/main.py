#region Imports and Setup
import os
import logging
from slack_bolt import App

# Python http.client libraries
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
jhnowURL = "jhnowdev.service-now.com"
jhnowAuthorization = os.environ.get("JHNOWDEV_AUTH") # This is found in GCP Secrets Manager

# Jira API stuff for Future Features
jira_authorization=os.environ.get("JIRA_AUTH") # This is found in GCP Secrets Manager
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
    conn = http.client.HTTPSConnection(jhnowURL)
    payload = json.dumps({
      "short_description": description,
      "description": f"Thread: {url} \nTask created by {reporter_email} from Slack. \nAssignee: {assignee_email} \nDescription: {description}",
      "assignment_group": "ae690fb24747f5d4629fd4f4126d434a", # Cloud Infrastructure - Pulsar Assinment Group sys_id in ServiceNow dev instance
      "active": True
    })
    headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Basic ' + jhnowAuthorization
    }
    conn.request("POST", "/api/now/table/sc_task", payload, headers)
    res = conn.getresponse()
    data = res.read()
    say(f"Ticket created for {assignee_email}! {data}", thread_ts=body["event"]["item"]["ts"])

    
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