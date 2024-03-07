#region Imports and Setup
import os
import logging
from slack_bolt import App

# Jira API stuff
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
jira_authorization=os.environ.get("JIRA_AUTH")
#endregion

#region Slash Command (/triage) Functionality
# This is the slash command. We are not really using it, but it will notify them on how to use the bot.
@app.command("/triage")
def hello_command(ack, logger):
  logger.info("I see a slash command!")
  ack("Hi from The Jira and Slack Integration bot! Use reactions to have me create (:eyes) or complete (:white_check_mark) a ticket.")
#endregion

#region Reaction_Removed Event Functionality
# @app.event("reaction_removed")
# def handle_reaction_removed(body, say, logger):
#   logger.info("I see a reaction_removed event!")
#   logger.info(body)
#   reaction = body["event"]["reaction"]
#   if reaction == "eyes":
#     say("You removed the :eyes: reaction. I will delete that ticket.")
#   if reaction == "white_check_mark":
#     say("You removed the :white_check_mark: reaction. I will reopen that ticket.")
#endregion

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
  
  # TODO: Don't allow this to be run from within a thread
  
  #region :eyes: Reaction Functionality (Create a ticket)
  if reaction == "eyes":
    say(f"Hey there <@{assignee}>! I will create a ticket for <@{reporter}> with a description of {description}!", thread_ts=body["event"]["item"]["ts"])
    
    # Confirmed that reporter_email and assignee_email is good. Using a dummy for testing.
    # TODO: Remove the dummy 
    reporter_email = "mreynolds@jackhenry.com"
    assignee_email = "pheintz@jackhenry.com"
    jiraReporterID = findJiraUserAccountID(reporter_email)
    jiraAssigneeID = findJiraUserAccountID(assignee_email)
    
    # TODO: Handle is the user is not found in Jira (only matters if they are not the assignee)
    createTicket(url, description, jiraReporterID, jiraAssigneeID)
    #endregion
  
  #region :white_check_mark: Reaction Functionality (Complete a ticket)
  elif reaction =="white_check_mark":
    say(f"Hey there <@{assignee}>! I will mark this ticket as done!", thread_ts=body["event"]["item"]["ts"])
  #endregion

#endregion

#region App_Mention (@Jira and Slack Integration) Event Functionality
@app.event("app_mention")
def event_test(say, logger):
  logger.info("I see a mention!")
  say("Hi there! I am The Jira and Slack Integration bot! Use reactions to have me create (:eyes) or complete (:white_check_mark) a ticket.")

def triage(req: Request):
  app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
  )
  return handler.handle(req)
#endregion

#region Jira API Functions
# Jira API functions
def findJiraUserAccountID(email):
  # This is the Jira API for finding a user's account ID
  conn = http.client.HTTPSConnection("banno-jha.atlassian.net")
  payload = ''
  headers = {
    'Authorization': 'Basic ' + jira_authorization
  }
  conn.request("GET", f"/rest/api/3/user/search?query=" + email, payload, headers)
  res = conn.getresponse()
  data = res.read()
  # Parse the JSON and return the account ID
  return json.loads(data.decode("utf-8"))[0]["accountId"]

def createTicket(url, description, jiraReporterID, jiraAssigneeID):
  conn = http.client.HTTPSConnection("banno-jha.atlassian.net")
  payload = json.dumps({
    "fields": {
      "project": {
        "key": "PULS"
      },
      "summary": url,
      "description": {
        "type": "doc",
        "version": 1,
        "content": [
          {
            "type": "paragraph",
            "content": [
              {
                "type": "text",
                "text": description
              }
            ]
          }
        ]
      },
      "issuetype": {
        "name": "Task"
      },
      "reporter": {
        "id": jiraReporterID
      },
      "assignee": {
        "accountId": jiraAssigneeID
      }
    }
  })
  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic ' + jira_authorization
  }
  conn.request("POST", "/rest/api/3/issue", payload, headers)
  res = conn.getresponse()
  data = res.read()
  print(data.decode("utf-8"))

#endregion