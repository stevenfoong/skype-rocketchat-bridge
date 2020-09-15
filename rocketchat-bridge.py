#!/usr/bin/env python3

import os
import sys
import requests
import json
import magic
import html
import markdown_strings as md
import pytz
import re

from skpy import Skype
from skpy import SkypeEventLoop
from skpy import SkypeNewMessageEvent
from skpy import SkypeEditMessageEvent
from skpy import SkypeContacts
from skpy import SkypeContactGroup
from skpy import SkypeMessageEvent
from skpy import SkypeConnection

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

sk=Skype(app_username, app_password,"/opt/skype-rocketchat-bridge/.tokens")
sk.chats

print("Skype to Rocket Chat Bridge Started")

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

    msg = re.sub('<(/)?ss( type="\w+")?>', '', msg)
    msg = msg.replace("</ss>","")

    msg = re.sub('<at [^>]*>', '*@', msg)
    msg = msg.replace("</at>","*")
    
    msg = re.sub('<a[^>]+href=\"(.*?)\"[^>]*>', '', msg)
    msg = msg.replace("</a>","")

    return msg

def process_quote_msg(msg,msg_id,msg_channel):
    soup = BeautifulSoup(msg, 'html.parser')
    q_msg = (soup.find('legacyquote').next_sibling)
    for msgs in sk.chats[msg_channel].getMsgs():
        if msgs.id == msg_id:
            q_msg = process_msg(msgs.content)
    return q_msg


class MySkype(SkypeEventLoop):
    def onEvent(self, event):
        if isinstance(event,(SkypeNewMessageEvent, SkypeEditMessageEvent, SkypeMessageEvent)):

            if os.path.exists('skype-bot.log'):
                logF = open("skype-bot.log", "a", encoding="utf-8")
            else:
                logF = open("skype-bot.log", "w", encoding="utf-8")

            log_prefix = event.msg.id

            logF.write(log_prefix + ": Start processing message." + '\n')
            logF.write(log_prefix + ": Message ID : " + event.msg.id + '\n')
            logF.write(log_prefix + ": Message type : " + event.msg.type + '\n')

            if hasattr(sk.contacts.user(event.msg.userId),'name'):
                sender_name = str(getattr(sk.contacts.user(event.msg.userId), 'name'))
                logF.write(log_prefix + ": Sender Id found : " + event.msg.userId + '\n')
                logF.write(log_prefix + ": Sender name found : " + sender_name + '\n')
            else:
                sender_name = event.msg.userId

            if hasattr(sk.contacts.user(event.msg.userId),'avatar'):
                sender_avatar = sk.contacts.user(event.msg.userId).avatar
                if sender_avatar is not None:
                    logF.write(log_prefix + ": Sender avatar found : " + sender_avatar + '\n')
            else:
                sender_avatar = "https://vignette.wikia.nocookie.net/logopedia/images/f/fb/Skype_Logo_2019.svg/revision/latest/scale-to-width-down/340?cb=20191207211056"

            if hasattr(sk.chats.chat(event.msg.chatId),'topic'):
                chattopic=sk.chats.chat(event.msg.chatId).topic
                logF.write(log_prefix + ": Chat Topic found : " + chattopic + '\n')
            else:
                chattopic="skype-bot-private-message"

            message_content = event.msg.content
            logF.write(log_prefix + ": Message Content : " + message_content + '\n')
            processed_message = process_msg(message_content)

            data_set = {
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

            print(event.msg)
            
            if (event.msg.type =="RichText/UriObject" or event.msg.type =="RichText/Media_GenericFile") and event.msg.userId != skype_bot_id:
                logF.write(log_prefix + ": Message File Name : " + event.msg.file.name + '\n')

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
                files = { 'file': (event.msg.file.name, open(event.msg.file.name, 'rb'),magic.from_file(event.msg.file.name, mime=True)),}
                bot_msg = {'msg' : 'File ' + magic.from_file(event.msg.file.name) + ' sent by ' + sender_name}
                upload_file = requests.post(api_url, data = bot_msg, headers = headers, files = files)
                logF.write(log_prefix + ": Upload File Status : " + str(upload_file.status_code) + '\n')
                if os.path.exists(event.msg.file.name):
                    os.remove(event.msg.file.name)
                    
            elif (event.msg.type =="RichText/Media_AudioMsg") and event.msg.userId != skype_bot_id:
                audio_msg = BeautifulSoup(event.msg.content, 'html.parser')
                if len(audio_msg.find_all('uriobject')) > 0:
                    attributes_dictionary = audio_msg.find('uriobject').attrs
                    audio_file_url = attributes_dictionary['url_thumbnail']

                download_conn = SkypeConnection()
                download_conn.setTokenFile("download_conn_token")
                download_conn.soapLogin(app_username,app_password)
                resp = download_conn("GET", audio_file_url, auth=SkypeConnection.Auth.SkypeToken)

                if len(audio_msg.find_all('originalname')) > 0:
                    attributes_dictionary = audio_msg.find('originalname').attrs
                    audio_file_name = attributes_dictionary['v']
                    open(audio_file_name,'wb').write(resp.content)
                    
                    logF.write(log_prefix + ": Message File Name : " + audio_file_name + '\n')

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
                    files = { 'file': (audio_file_name, open(audio_file_name, 'rb'),magic.from_file(audio_file_name, mime=True)),}    
                    bot_msg = {'msg' : 'File ' + magic.from_file(audio_file_name) + ' sent by ' + sender_name + '\n' +
                                'If the audio file is not complete, please hear it at the skype web or skype client.'
                              }
                    upload_file = requests.post(api_url, data = bot_msg, headers = headers, files = files)
                    logF.write(log_prefix + ": Upload File Status : " + str(upload_file.status_code) + '\n')
                    
                    if os.path.exists(audio_file_name):
                        os.remove(audio_file_name)

            else:
                SoupText = BeautifulSoup(processed_message, 'html.parser')
                if len(SoupText.find_all('quote')) > 0:
                    attributes_dictionary = SoupText.find('quote').attrs
                    tz = pytz.timezone('Asia/Kuala_Lumpur')
                    ts = datetime.fromtimestamp(int(attributes_dictionary['timestamp']), tz)
                    quote_orig_msg_id = attributes_dictionary['messageid']
                    quote_author = attributes_dictionary['authorname']
                    quote_msg_timestamp = ts.strftime('%Y-%m-%d %H:%M:%S %Z')
                    quote_channel = event.msg.chatId

                    new_msg = SoupText.find('quote').next_sibling
                    quote_msg = process_quote_msg(processed_message,quote_orig_msg_id,quote_channel)

                    data_set_attachment = {
                        "text": new_msg,
                        "attachment": {
                            "color": '#0000DD',
                            "title": quote_author + " @ " + quote_msg_timestamp,
                            "text": quote_msg
                        }
                    }
                    data_set.update(data_set_attachment)

                json_dump = json.dumps(data_set)
                logF.write(log_prefix + ": Message Sent : " + json_dump + '\n')

                if event.msg.userId != skype_bot_id:
                    send_message = requests.post(rocketchat_url,data=json_dump)
                    logF.write(log_prefix + ": Send Message Status : " + str(send_message.status_code) + '\n')

            logF.write("\n")

            logF.close()

sk = MySkype(tokenFile="/opt/skype-rocketchat-bridge/.tokens", autoAck=True)
sk.loop()
