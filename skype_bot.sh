#!/bin/bash

export SKYPE_USERNAME="[skype username]"
export SKYPE_PASSWORD="[skype password]"
export SKYPE_BOT_ID="[skype bot ID]"

export ROCKETCHAT_URL="[rocket chat webhook url]"
export ROCKETCHAT_API="[rocket chat api url]"
export ROCKETCHAT_X_Auth_Token="[rocket chat bot token]"
export ROCKETCHAT_X_User_Id="[rocket chat bot id]"

clear

case $1 in

  list-recent-chat)
    ./skype_list_recent.chat.py
    ;;
  
  rocketchat-bridge)
    ./skype-rocketchat-bridge.py
    ;;

  retrieve-skype-bot-id)
    ./skype-bot-id.py
    ;;

  retrieve-rocketchat-account-id)
    ./rocketchat-account-id.py
    ;;
  
  *)
    echo -n "unknown parameter"
    ;;
    
esac
