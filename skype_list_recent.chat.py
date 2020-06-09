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

# for debug purpose
# print(f"username: {app_username}")
# print(f"password: {app_password}")

sk=Skype(app_username, app_password,".tokens")
sk.chats

for chat in sk.chats.recent():
    if hasattr(sk.chats.chat(chat),'topic'):
        chattopic=sk.chats.chat(chat).topic
        print("Chat Topic : ",chattopic)
    print("Chat ID : ",chat)
    print("\n")
