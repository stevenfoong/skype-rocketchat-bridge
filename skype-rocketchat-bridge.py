#!/usr/bin/env python3

import os
import sys
import requests
import json
import magic
import html
import markdown_strings as md
import pytz

from skpy import Skype
from skpy import SkypeEventLoop
from skpy import SkypeNewMessageEvent
from skpy import SkypeEditMessageEvent
from skpy import SkypeContacts
from skpy import SkypeContactGroup

from bs4 import BeautifulSoup

from datetime import datetime

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
    print("missing config ROCKETCHAT_URL")
    sys.exit(1)

skype_bot_id =  os.environ.get("SKYPE_BOT_ID")
if not skype_bot_id:
    print("missing config SKYPE_BOT_ID")
    sys.exit(1)

rocketchat_api =  os.environ.get("ROCKETCHAT_API")
if not rocketchat_api:
    print("missing config ROCKETCHAT_API")
    sys.exit(1)

rocketchat_x_auth_token =  os.environ.get("ROCKETCHAT_X_Auth_Token")
if not rocketchat_x_auth_token:
    print("missing config ROCKETCHAT_X_Auth_Token")
    sys.exit(1)

rocketchat_x_user_id =  os.environ.get("ROCKETCHAT_X_User_Id")
if not rocketchat_x_user_id:
    print("missing config ROCKETCHAT_X_User_Id")
    sys.exit(1)

# Remove to show debug info
debug = "true"

# print(f"username: {app_username}")
# print(f"password: {app_password}")

sk=Skype(app_username, app_password,".tokens")
sk.chats

def process_msg(msg):

    msg = msg.replace("<b raw_pre=\"*\" raw_post=\"*\">","*")
    msg = msg.replace("</b>","*")

    msg = msg.replace("<i raw_pre=\"_\" raw_post=\"_\">","_")
    msg = msg.replace("</i>","_")

    msg = msg.replace("<s raw_pre=\"~\" raw_post=\"~\">","~")
    msg = msg.replace("</s>","~")

    msg = msg.replace("<pre raw_pre=\"!! \">","")
    msg = msg.replace("<pre raw_pre=\"{code}\" raw_post=\"{code}\">","")
    msg = msg.replace("</pre>","")

    return msg

def quote_msg(msg,msg_id,msg_channel):
    #global quote_author, quote_msg_timestamp
    #soup = BeautifulSoup(msg, 'html.parser')
    #print (soup.find('legacyquote').next_sibling)
    msg_array = msg.split()
    #print (msg_array)
    q_msg = msg_array[3]
    #print ("quote orig msg id:")
    #print (quote_orig_msg_id)
    for msgs in sk.chats[msg_channel].getMsgs():
        #print(msgs.id)
        if msgs.id == msg_id:
            #print ("msg id:")
            #print(msgs.id)
            #print ("msg content:")
            print(msgs.content)
            soup = BeautifulSoup(msgs.content, 'html.parser')
            if len(soup.find_all('quote')) > 0:
                q_msg = soup.find('quote').next_sibling
            else:
                q_msg = msgs.content
    soup_quote = BeautifulSoup(q_msg, 'html.parser')
    print(q_msg)
    #qmsg = send_msg + "```&#x25B6; \n &#09;" + soup_quote.get_text() + "\n &#09;" + quote_author + " , " + quote_msg_timestamp + "```"
    # qmsg = msg + "\n &#62; quote msg \n" + quote_author + " , " + quote_msg_timestamp 
    return q_msg


class MySkype(SkypeEventLoop):
    def onEvent(self, event):
        if isinstance(event,(SkypeNewMessageEvent, SkypeEditMessageEvent)):

            if os.path.exists('skype-bot.log'):
                logF = open("skype-bot.log", "a")
            else:
                logF = open("skype-bot.log", "w")

            if hasattr(sk.contacts.user(event.msg.userId),'avatar'):
                #print("Avatar :",sk.contacts.user(event.msg.userId).avatar)
                sender_avatar = sk.contacts.user(event.msg.userId).avatar
            else:
                sender_avatar = "https://vignette.wikia.nocookie.net/logopedia/images/f/fb/Skype_Logo_2019.svg/revision/latest/scale-to-width-down/340?cb=20191207211056"

            if hasattr(sk.contacts.user(event.msg.userId),'name'):
                #print("Name :",sk.contacts.user(event.msg.userId).name)
                sender_name = str(getattr(sk.contacts.user(event.msg.userId), 'name'))
            else:
                sender_name = event.msg.userId
            
            if hasattr(sk.chats.chat(event.msg.chatId),'topic'):
                chattopic=sk.chats.chat(event.msg.chatId).topic
                #print("Chat Topic : ",chattopic)
            else:
                chattopic="skype-bot-private-message"
            
            message_content = event.msg.content
            processed_message = process_msg(message_content)

            if event.msg.type =="RichText/UriObject" or event.msg.type =="RichText/Media_GenericFile":

                if debug:
                    print("Message File:",event.msg.file)
                    print("Message File Name:",event.msg.file.name)

                file_attach = open(event.msg.file.name,"wb")
                file_attach.write(event.msg.fileContent)
                file_attach.close()

                api_url = rocketchat_api+"rooms.info?roomName="+chattopic
                X_Auth_Token="'X-Auth-Token': '" + rocketchat_x_auth_token + "'"
                X_User_Id="'X-User-Id': '" + rocketchat_x_user_id + "'"

                contentType="Content-Type:text/plain"
                
                headers = {'X-Auth-Token' : rocketchat_x_auth_token , 'X-User-Id' : rocketchat_x_user_id }
                room_info = requests.get(api_url, headers = headers)

                parsed_json = (json.loads(room_info.text))
                room = parsed_json['room']
                room_id = room['_id']

                api_url = 'https://chat.majasolutions.net/api/v1/rooms.upload/'+room_id
                # print (magic.from_file(event.msg.file.name, mime=True))
                files = { 'file': (event.msg.file.name, open(event.msg.file.name, 'rb'),magic.from_file(event.msg.file.name, mime=True)),}    
                bot_msg = {'msg' : 'File ' + magic.from_file(event.msg.file.name) + ' sent by ' + sender_name}
                upload_file = requests.post(api_url, data = bot_msg, headers = headers, files = files)
                #print(upload_file.text)
                if os.path.exists(event.msg.file.name):
                    os.remove(event.msg.file.name)

            SoupText = BeautifulSoup(message_content, 'html.parser')
            if len(SoupText.find_all('quote')) > 0:
                attributes_dictionary = SoupText.find('quote').attrs
                tz = pytz.timezone('Asia/Kuala_Lumpur')
                ts = datetime.fromtimestamp(int(attributes_dictionary['timestamp']), tz)
                quote_orig_msg_id = attributes_dictionary['messageid']
                quote_author = attributes_dictionary['authorname']
                quote_msg_timestamp = ts.strftime('%Y-%m-%d %H:%M:%S %Z')
                quote_channel = event.msg.chatId
                print ("real quote message :",quote_msg(message_content,quote_orig_msg_id,quote_channel))

            data_set = {
                #"text": html.unescape(event.msg.content),
                #"text": html.unescape(format_msg(tag_format,soup.get_text())),
                "text": processed_message,
                "avatar": sender_avatar,
                "channel": chattopic,
                "from":{
                    "id":event.msg.userId,
                    "name":sender_name
                },
                "conversation": {
                    "id":event.msg.chatId
                }
            }

            json_dump = json.dumps(data_set)
            #print(json_dump)
            if event.msg.userId != skype_bot_id:
                r=requests.post(rocketchat_url,data=json_dump)
                if r.status_code != 200:
                    logF.write(" Send Message failed. \n")
                    # print("failed")

                    logF.write("\n")

            if debug:
                print("Chat Topic :",chattopic)
                print("Chat ID :",event.msg.chatId)
                print("Message ID :",event.msg.id)
                print("User ID :",event.msg.userId)
                print("User Name :",sender_name)
                print("User Avartar :",sender_avatar)
                #print("Message :",event.msg.content)
                print("Message :",message_content)
                print("Message Type:",event.msg.type)
                print("Message Sent:",processed_message)
                

            logF.write("Chat Topic :" + chattopic + '\n')
            logF.write("Chat ID :" + event.msg.chatId + '\n')
            logF.write("Message ID :" + event.msg.id + '\n')
            logF.write("User ID :" + event.msg.userId + '\n')
            logF.write("User Name :" + sender_name + '\n')
            logF.write("User Avartar :" + sender_avatar + '\n')
            logF.write("Message :" + message_content + '\n')
            logF.write("Message Type :" + event.msg.type + '\n')
            logF.write("Message Sent :" + processed_message + '\n')

            logF.close()

sk = MySkype(tokenFile=".tokens", autoAck=True)
sk.loop()
