#!/bin/bash

export SKYPE_USERNAME="[skype username]"
export SKYPE_PASSWORD="[skype password]"
export ROCKETCHAT_URL="[rocket chat webhook url]"
export SKYPE_BOT_ID="[skype bot ID]"
clear

case $1 in

  list-recent-chat)
    ./skype_list_recent.chat.py
    ;;
  
  rocketchat-bridge)
    ./skype-rocketchat-bridge.py
    ;;
  
  *)
    echo -n "unknown parameter"
    ;;
    
esac
