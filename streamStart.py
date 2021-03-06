#!/usr/bin/python
# vim: tabstop=4 expandtab shiftwidth=2 softtabstop=2

import httplib2
import os
import sys
import csv
from datetime import datetime
import json
import pytz
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))
local = pytz.timezone ("Europe/Prague")
streams = [[],[]]
broadcasts = [[],[]]

def myconverter(o):
    if isinstance(o, datetime):
      return o.strftime("%Y-%m-%dT%H:%M:%S+01:00")

def get_authenticated_service():
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_READ_WRITE_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, None)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

youtube = get_authenticated_service()

list_broadcasts_response = youtube.liveBroadcasts().list(
broadcastStatus="upcoming",
part="id,snippet,status",
maxResults=4
).execute()

result=[]
for broadcast in list_broadcasts_response.get("items", []):
  print broadcast['snippet']['title'] + " " + broadcast['snippet']['scheduledStartTime']
  transition_result = youtube.liveBroadcasts().transition(
      broadcastStatus='testing',
      id=broadcast['id'],
      part='id,snippet,status'
  ).execute()
  result.append(transition_result)

while True:
  for res in result:
    print "index " + str(result.index(res))
    print res
    if res['status']['lifeCycleStatus'] == 'testStarting':
      continue
    else:
      print res['id']
      print "Going Live"
      transition_result = youtube.liveBroadcasts().transition(
          broadcastStatus='live',
          id=broadcast['id'],
          part='id,snippet'
      ).execute()
      print transition_result
      result.pop(result.index(res))
      if len == 0:
        break
  time.sleep(2)

#    print "len " + str(len(result))
#
#
#
#  print "details"
#  get_stream = youtube.liveBroadcasts().list(
#    part="id,snippet,contentDetails,status",
#    id=transition_result['id']
#  ).execute()
#  print get_stream

#  print transition_result
#  time.sleep(10)
#  print "Going Live"
#  transition_result = youtube.liveBroadcasts().transition(
#      broadcastStatus='live',
#      id=broadcast['id'],
#      part='id,snippet'
#  ).execute()
#  print transition_result
