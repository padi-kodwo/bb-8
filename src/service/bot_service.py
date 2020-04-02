import json
import logging as logger
import logging.config
import requests
import time

import system_paths
from src import util

# configure the logging format
from src.model import Emoji
from src.service.request import Dialogflow

logger.config.fileConfig(system_paths.resource + "/config/logger.conf")


def get_reply(message, session_id):
    response_text = None

    if message is not None:
        logger.info("[ " + session_id + " ] about to call dialog flow for " + str(message))

        if "genre=" in message:

            response_text_list = message.split("=")
            response_text = response_text_list[1].strip(" ")
            return response_text, "genre_carousel_reply"

        elif "newsbot" in message.replace(" ", "").lower():
            return response_text, "greetings_quick_reply"

        elif "iwantmore" in message.replace(" ", "").lower():
            return response_text, "greetings_quick_reply"

        elif "news" == message.replace(" ", "").lower():
            return response_text, "greetings_quick_reply"

        else:
            dialog_flow_obj = Dialogflow(message)
            dialog_flow_respond = dialog_flow_obj.get_kb_response()

            logger.info("[ " + session_id + " ] about to get bot response")

            emoji = Emoji()

            if dialog_flow_respond.query_result.action == "date.get":
                response_text = date_processing()

            elif dialog_flow_respond.query_result.fulfillment_text is None or dialog_flow_respond.query_result.fulfillment_text is "":
                logger.info("[ " + session_id + " ] response fulfilment was empty or None")
                response_text = "Haha haha haha"

            elif dialog_flow_respond.query_result.action == "smalltalk.greetings.hello":
                greeting_trigger_list = util.get_property(property_section="botSection", property_name="bot.greeting.triggers").split(",")
                logger.info("[ " + session_id + " ] small talk hello triggered with message " + message)

                if message.lower() in greeting_trigger_list:
                    response_text = "Hey " + emoji.waving_hand + ", news nerd " + emoji.nerd_face + ".\nI'm now a paperboy too" + \
                                    emoji.paper_boy + " aside your chat companion.\nRemember to say 'news bot' for the news " + emoji.new_paper

                    # build greetings quick reply
                    return response_text, None
                else:
                    response_text = dialog_flow_respond.query_result.fulfillment_text

            elif dialog_flow_respond.query_result.fulfillment_text:
                response_text = dialog_flow_respond.query_result.fulfillment_text

    else:
        disappointed_face = u"\U0001F61E"
        response_text = "really? ..." + disappointed_face

    logger.info("[ " + session_id + " ] done getting reply message for message" + message)

    return response_text, None


def send_message(recipient_id, message, session_id):
    logger.info("[ " + session_id + " ] about to send message to recipient ")

    access_token = util.get_property(property_section="facebookSection", property_name="fb.access.token")
    url = util.get_property(property_section="facebookSection", property_name="fb.messages.url")

    params = {
        "access_token": access_token
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message
        }
    })

    logger.info("[ " + session_id + " ] message to be sent is " + str(data))

    time.sleep(2)

    fb_response = requests.post(url=url, params=params, headers=headers, data=data)

    logger.info("[ " + session_id + " ] message response " + str(fb_response.content))

    return


def send_template(message, session_id):
    logger.info("[ " + session_id + " ] about to send template reply " + message)

    access_token = util.get_property(property_section="facebookSection", property_name="fb.access.token")
    url = util.get_property(property_section="facebookSection", property_name="fb.messages.url")

    params = {
        "access_token": access_token
    }

    headers = {
        "Content-Type": "application/json"
    }

    time.sleep(4)
    fb_response = requests.post(url=url, params=params, headers=headers, data=message)

    logger.info("[ " + session_id + " ] message response " + str(fb_response.content))

    return


def send_thinking_typing(recipient_id, session_id):
    logger.info("[ " + session_id + " ] about to send message read")

    access_token = util.get_property(property_section="facebookSection", property_name="fb.access.token")
    url = util.get_property(property_section="facebookSection", property_name="fb.messages.url")

    params = {
        "access_token": access_token
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "sender_action": "typing_on"  # typing_off
    })

    time.sleep(2)
    fb_response = requests.post(url=url, params=params, headers=headers, data=data)

    logger.info("[ " + session_id + " ] message response " + str(fb_response.content))

    return


def send_read(recipient_id, session_id):
    logger.info("[ " + session_id + " ] about to send typing dots")

    access_token = util.get_property(property_section="facebookSection", property_name="fb.access.token")
    url = util.get_property(property_section="facebookSection", property_name="fb.messages.url")

    params = {
        "access_token": access_token
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "sender_action": "mark_seen"  # typing_off
    })

    time.sleep(2)
    fb_response = requests.post(url=url, params=params, headers=headers, data=data)

    logger.info("[ " + session_id + " ] message response " + str(fb_response.content))

    return


def date_processing():
    import datetime
    date_time_obj = datetime.datetime.now()
    bot_date_response = date_time_obj.strftime("%B %d, %Y, %H:%M:%S")
    return bot_date_response
