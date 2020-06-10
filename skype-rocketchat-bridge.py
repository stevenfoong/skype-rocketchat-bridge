#!/usr/bin/env python3

import os
import sys
from skpy import Skype

app_username = os.environ.get("SKYPE_USERNAME")
if not app_username:
    print("missing config SKYPE_USERNAME")
    sys.exit(1)

app_password = os.environ.get("SKYPE_PASSWORD")
if not app_password:
    print("missing config SKYPE_PASSWORD")
    sys.exit(1)

rocketchat_url = os.environ.get("ROCKETCHAT_URL")
if not rocketchat_url:
    print("ROCKETCHAT_URL")
    sys.exit(1)

skype_bot_id =  os.environ.get("SKYPE_BOT_ID")
if not skype_bot_id:
    print("missing config SKYPE_BOT_ID")
    sys.exit(1)
    
# for debug purpose
# print(f"username: {app_username}")
# print(f"password: {app_password}")

from skpy import Skype
from skpy import SkypeEventLoop,SkypeNewMessageEvent,SkypeContactGroup,SkypeEditMessageEvent
from skpy import SkypeContacts
import requests
import json

sk=Skype(app_username, app_password,".tokens")
sk.chats

class MySkype(SkypeEventLoop):
    def onEvent(self, event):
        if isinstance(event,(SkypeNewMessageEvent, SkypeEditMessageEvent)):
        
            if hasattr(sk.contacts.user(event.msg.userId),'avatar'):
                print("Avatar :",sk.contacts.user(event.msg.userId).avatar)
                sender_avatar = sk.contacts.user(event.msg.userId).avatar
            else:
                sender_avatar = "https://vignette.wikia.nocookie.net/logopedia/images/f/fb/Skype_Logo_2019.svg/revision/latest/scale-to-width-down/340?cb=20191207211056"

            if hasattr(sk.contacts.user(event.msg.userId),'name'):
                print("Name :",sk.contacts.user(event.msg.userId).name)
                sender_name = str(getattr(sk.contacts.user(event.msg.userId), 'name'))
            else:
                sender_name = event.msg.userId

            if hasattr(sk.chats.chat(event.msg.chatId),'topic'):
                chattopic=sk.chats.chat(event.msg.chatId).topic
                print("Chat Topic : ",chattopic)
            else:
                chattopic="skype-bot-private-message"

            data_set = {
                "text": event.msg.content,
                "avatar": sender_avatar,
                "channel": chattopic,
                #"sender_name": sender_name,
                "from":{
                    "id":event.msg.userId,
                    "name":sender_name
                },
                "conversation": {
                    "id":event.msg.chatId
                }
            }

            json_dump = json.dumps(data_set)
            r=requests.post(rocketchat_url,data=json_dump)
            if r.status_code != 200:
                print("failed")
                
sk = MySkype(tokenFile=".tokens", autoAck=True)
sk.loop()
