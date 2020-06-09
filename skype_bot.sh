#!/bin/bash

export SKYPE_USERNAME="[skype username]"
export SKYPE_PASSWORD="[skype password]"
clear

case $1 in

  list-recent-chat)
    ./skype_list_recent.chat.py
    ;;
  
  *)
    echo -n "unknown parameter"
    ;;
    
esac
