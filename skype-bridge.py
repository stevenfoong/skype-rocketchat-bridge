#!/usr/bin/env python3

import os
import sys
import requests
import datetime
import base64

import flask
from flask import request, jsonify

import json

skype_bot_id = os.environ.get("SKYPE_BOT_ID")
if not skype_bot_id:
    print("missing config SKYPE_BOT_ID")
    sys.exit(1)

skype_bot_app_secret = os.environ.get("SKYPE_BOT_SECRET")
if not skype_bot_app_secret:
    print("missing config SKYPE_BOT_SECRET")
    sys.exit(1)

rocketchat_domain = os.environ.get("ROCKETCHAT_DOMAIN")
if not rocketchat_domain:
    print("missing config ROCKETCHAT_DOMAIN")
    sys.exit(1)

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def s_channel_id(channel_name):
    switcher={
           'channel-1':'ID1',
           'channel-2':'ID2'
    }
    return switcher.get(channel_name,"Unknown")

@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"

@app.route('/incoming', methods=['POST'])
def msg_incoming():
    data = request.get_json()
    if ((data["bot"] == False) and (s_channel_id(data["channel_name"]) != "Unknown")) :
        url="https://login.microsoftonline.com/common/oauth2/v2.0/token"
        credential_data = {
            "grant_type":"client_credentials",
            "client_id":skype_bot_id,
            "client_secret":skype_bot_app_secret,
            "scope":"https://api.botframework.com/.default"
        }
        response = requests.post(url,credential_data)
        resData = response.json()
        if "message" in data:
            if "_id" in data["message"]["file"]:
                fileURL = "https://" + rocketchat_domain + "/file-upload/" + data["message"]["file"]["_id"] + "/" + data["message"]["file"]["name"]
                attachment = requests.get(fileURL, allow_redirects=True)
                filename = data["message"]["file"]["name"]
                responseURL = "https://smba.trafficmanager.net/apis/v3/conversations/" + s_channel_id(data["channel_name"]) + "/activities/"
                MessageSent = requests.post(
                    responseURL,
                    json={
                        "textFormat": "plain",
                        "type": "message",
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%zZ"),
                        "channelId": "skype",
                        "conversation": {
                            "id": s_channel_id(data["channel_name"])
                        },
                        "from": {
                            "id": skype_bot_id,
                            "name": "mjcs"
                        },
                        "attachments": [
                            {
                                "contentType": data["message"]["file"]["type"],
                                "contentUrl": "data:" + data["message"]["file"]["type"] + ";base64," + (base64.b64encode(attachment.content).decode("utf-8")),
                                "name": data["message"]["file"]["name"]
                            }
                        ],
                    },
                    headers={
                        "Authorization":"%s %s" % (resData["token_type"],resData["access_token"])
                    }
                )
            print (MessageSent.status_code)

        if data["text"] != "":
            responseURL = "https://smba.trafficmanager.net/apis/v3/conversations/" + s_channel_id(data["channel_name"]) + "/activities/"
            MessageSent = requests.post(
                responseURL,
                json={
                    "textFormat": "plain",
                    "type": "message",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%zZ"),
                    "channelId": "skype",
                    "conversation": {
                        "id": s_channel_id(data["channel_name"])
                    },
                    "from": {
                        "id": skype_bot_id,
                        "name": "mjcs"
                    },
                    "text": data["text"]
                },
                headers={
                    "Authorization":"%s %s" % (resData["token_type"],resData["access_token"])
                }
            )
            print (MessageSent.status_code)


    return "Completed"

app.run(host="0.0.0.0")
