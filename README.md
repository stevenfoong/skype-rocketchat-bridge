# [Bridge between Skype and Rocketchat container](https://hub.docker.com/r/stevenfoong/skype-rocketchat-bridge)
![alt text](https://img.shields.io/docker/automated/stevenfoong/skype-rocketchat-bridge.svg)

## What?
A bridge between skype and rocketchat writing in python. Bridge from Skype to RocketChat is using [SkPy Library](https://github.com/Terrance/SkPy). Bridge from RocketChat to Skype is python script build from scratch connect Azure Bot API.

## How?
Configure through these environment variables:
* `SKYPE_USERNAME` : The user name to authenticate with skype.
* `SKYPE_PASSWORD` : The password to authenticate with skype.
* `SKYPE_BOT_ID` : The skype bot id in azure. Refer to [Bridge between Skype and Rocketchat container](https://github.com/stevenfoong/skype-rocketchat-bridge/wiki) on how to find this skype bot id.
* `SKYPE_BOT_SECRET` : The skype bot secret in azure. Refer to [Bridge between Skype and Rocketchat container](https://github.com/stevenfoong/skype-rocketchat-bridge/wiki) on how to generate skype bot id.
* `ROCKETCHAT_URL` : The webhook URL that use to send message from skype to rocketchat. Refer to [Bridge between Skype and Rocketchat container](https://github.com/stevenfoong/skype-rocketchat-bridge/wiki) on how to find this webhook URL.
* `ROCKETCHAT_API` : The API URL that use to upload attachment. Refer to [Bridge between Skype and Rocketchat container](https://github.com/stevenfoong/skype-rocketchat-bridge/wiki) on how to find this webhook URL.
* `ROCKETCHAT_DOMAIN` : Rocket chat domain name.
* `ROCKETCHAT_X_Auth_Token` : Token of bot account in Rocketchat. Refer to [Bridge between Skype and Rocketchat container](https://github.com/stevenfoong/skype-rocketchat-bridge/wiki) on how to create the token.
* `ROCKETCHAT_X_User_Id` : Bot account in Rocketchat. Refer to [Bridge between Skype and Rocketchat container](https://github.com/stevenfoong/skype-rocketchat-bridge/wiki) on how to create the bot account.

## Running this image with docker-compose

The volumes are set to keep the channel mapping file persistent. If you dont need the bridge from rocketchat to skype or you don't mind update the channel mapping file everytime after you update the image, you can remove the volume section.

```
version: '3'
services:
  skype-rocketchat-bridge:
    image: stevenfoong/skype-rocketchat-bridge
    container_name: skype-rocketchat-bridge
    restart: always
    ports:
      - 5000:5000
    environment:
     - SKYPE_USERNAME=[skype username]
     - SKYPE_PASSWORD=[skype password]
     - SKYPE_BOT_ID=[skype bot ID]
     - SKYPE_BOT_SECRET=[skype bot secret token]
     - ROCKETCHAT_URL=[rocket chat webhook url]
     - ROCKETCHAT_API=[rocket chat api url]
     - ROCKETCHAT_DOMAIN=rocket chat domain
     - ROCKETCHAT_X_Auth_Token=[rocket chat bot token]
     - ROCKETCHAT_X_User_Id=[rocket chat bot id]
    volumes:
     - /data/skype-rocketchat-bridge:/opt/skype-rocketchat-bridge/data
```

## Need Help ?

If you have any question or facing any issue setup the container, raise an [issue](https://github.com/stevenfoong/skype-rocketchat-bridge/issues), i will try my best to answer your question or help you out.
