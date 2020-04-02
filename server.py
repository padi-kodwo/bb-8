# server.py
import json
import logging as logger
import logging.config
import threading
import time

from flask import Flask, render_template, request
from flask_cors import CORS
from waitress import serve

import system_paths

# creates a Flask application, named app
from src import util
from src import model
from src.service import bot_service

app = Flask(__name__)

CORS(app)
# configure the logging format
logger.config.fileConfig(system_paths.resource + "/config/logger.conf")


@app.route("/")
def home():
    host_address = util.get_property("serverSection", "host.address")
    return render_template("index.html", host_address=host_address)


@app.route("/api/v1/bot", methods=["GET"])
def verify():
    session_id = util.session_id()
    logger.info("[ " + session_id + " ] about to process bot request " + str(request.json))

    # when the endpoint is registered as a web hook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        verification_token = util.get_property(property_section="facebookSection", property_name="fb.verification.token")

        if not request.args.get("hub.verify_token") == verification_token:
            logger.warning("[ " + session_id + " ] verification from facebook failed ")
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello, world!", 200


@app.route("/api/v1/bot", methods=["POST"])
def bot_controller():
    session_id = util.session_id()
    logger.info("[ " + session_id + " ] about to process bot request " + str(request.json))

    data = request.json

    if data["object"] == "page":
        for entry in data["entry"]:
            logger.info("here " + str(entry))
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent the bot a message

                    sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending the message

                    bot_service.send_read(sender_id, session_id)

                    logger.info("[ " + session_id + " ] about to process incoming message " + str(messaging_event["message"]))

                    # threading the bot read message state to reduce latency
                    thread = threading.Thread(target=bot_service.send_thinking_typing, args=(sender_id, session_id,))
                    thread.start()

                    message = messaging_event["message"]
                    message_text = message["text"]  # the message's text
                    message_payload = message.get("quick_reply") if message.get("quick_reply") is not None else message_text

                    if isinstance(message_payload, str):
                        pass
                    else:
                        message_payload = message_payload.get("payload") if message_payload.get("payload") is not None else message_payload

                    message_reply, message_intent = bot_service.get_reply(message=message_payload, session_id=session_id)

                    if message_intent is "greetings_quick_reply":

                        logger.info(
                            "[ " + session_id + " ] greetings code triggered, about to send greeting quick replies ")

                        quick_reply_message = model.get_greeting_quick_links(recipient=sender_id)
                        bot_service.send_template(message=json.dumps(quick_reply_message.__dict__),
                                                  session_id=session_id)

                    elif message_intent is "genre_carousel_reply":
                        logger.info("[ " + session_id + " ] about send genre carousel request for " + message_reply)

                        carousel_reply = model.get_genre_templates(recipient_id=sender_id, genre=message_reply, session_id=session_id)
                        bot_service.send_template(message=carousel_reply, session_id=session_id)

                    elif message_text is not None:
                        bot_service.send_message(recipient_id=sender_id, message=message_reply, session_id=session_id)

                        logger.info("[ " + session_id + " ] response sent for " + message_text)
                    else:
                        pass

                elif messaging_event.get("delivery"):  # delivery confirmation
                    pass

                elif messaging_event.get("optin"):  # opt in confirmation
                    pass

                elif messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message

                    message = messaging_event["postback"]

                    if message.get("payload"):
                        if "ok" in message["payload"]:
                            sender_id = messaging_event["sender"]["id"]

                            bot_service.send_read(sender_id, session_id)

                            # threading the bot read message state to reduce latency
                            thread = threading.Thread(target=bot_service.send_thinking_typing, args=(sender_id, session_id,))
                            thread.start()

                            time.sleep(2)

                            bot_service.send_message(recipient_id=sender_id, message="ayt", session_id=session_id)

                    pass

    return "ok", 200


# run the application
if __name__ == "__main__":
    server_type = "flask"
    host = util.get_property(property_section="serverSection", property_name="host.name")
    port = util.get_property(property_section="serverSection", property_name="host.port")

    if server_type is "flask":
        logger.info("about to launch app on " + server_type)
        app.run(debug=True, host=host, port=port)    # using the default
    elif server_type is "waitress":
        serve(app, host=host, port=port)