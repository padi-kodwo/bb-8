import json
from src import util
from src.service import news_service


class QuickReplies:
    def __init__(self, content_type, title, payload, image_url):
        self.content_type = content_type
        self.title = title
        self.payload = payload
        self.image_url = image_url


class Message:
    def __init__(self, text, quick_replies, attachment):
        self.text = text
        self.quick_replies = quick_replies
        self.attachment = attachment


class Recipient:
    def __init__(self, id):
        self.id = id

    def to_json(self):
        data = json.dumps({
                "id": self.id
            })

        return data


class FacebookMessage:
    def __init__(self, recipient, messaging_type, message, sender_action):
        self.recipient = recipient
        self.messaging_type = messaging_type
        self.message = message
        self.sender_action = sender_action


def get_greeting_quick_links(recipient):
    genres = util.get_property(property_section="genresConfig", property_name="genres.list")
    genres_list = genres.split(",")
    quick_replies_list = []

    emoji = Emoji()

    for genre in genres_list:
        if genre is not None:
            payload = "genre=" + genre
            quick_reply = QuickReplies(content_type="text", title=genre.title(), payload=payload, image_url=None)
            del quick_reply.image_url
            quick_reply_json = json.dumps(quick_reply.__dict__)
            quick_replies_list.append(quick_reply_json)

    quick_reply_message_ = "what would interest you?" + emoji.questioning
    message = Message(text=quick_reply_message_, quick_replies=quick_replies_list, attachment="None")
    del message.attachment
    message = json.dumps(message.__dict__)

    recipient = Recipient(recipient)
    print(recipient.to_json())

    facebook_message = FacebookMessage(recipient=recipient.to_json(), messaging_type="RESPONSE", message=message, sender_action=None)
    del facebook_message.sender_action

    return facebook_message


class Emoji:
    def __init__(self):
        self.sports = u"\U000026BD"
        self.finance = u"\U0001F4B0"
        self.science = u"\U0001F9EA"
        self.technology = u"\U0001F4BB"
        self.interesting_face = u"\U0001F9D0"
        self.questioning = u"\U0001F914"
        self.paper_boy = u"\U0001F6B4"
        self.nerd_face = u"\U0001F913"
        self.waving_hand = u"\U0001F44B"
        self.new_paper = u"\U0001F4F0"


def get_genre_templates(recipient_id, genre, session_id):

    news_api_genres_list = util.get_property(property_section="newsApiSection", property_name="news.api.genres.list").split(",")

    if genre.lower() in news_api_genres_list:
        elements = get_from_news_api(genre, session_id)
    else:
        elements = get_from_nyt_api(genre, session_id)

    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": elements
                }
            }
        }
    }

    return json.dumps(data)


def get_from_news_api(genre, session_id):
    response = news_service.get_news_api_news(genre, session_id)
    response_results = response["articles"]

    # default_news_image = util.get_property(property_section="serverSection", property_name="server.address.url")
    default_news_image = util.get_property(property_section="imageSection", property_name="default.news.image")

    elements = []

    count = 0
    for result in response_results:
        if count < 10:

            buttons = [
                {
                    "type": "web_url",
                    "url": result["url"],
                    "title": "read story"
                }, {
                    "type": "postback",
                    "title": "Continue Chatting",
                    "payload": "ok"
                }
            ]

            image_url = result.get("urlToImage")
            if image_url == "null" or image_url is None:
                image_url = default_news_image

            element = {
                "title": result["title"],
                "image_url": image_url,
                "subtitle": result["description"],
                "default_action": {
                    "type": "web_url",
                    "url": result["url"],
                    "webview_height_ratio": "tall",
                },
                "buttons": buttons
            }

            elements.append(element)

            count += 1
        else:
            break

    return elements


def get_from_nyt_api(genre, session_id):
    response = news_service.get_nyt_news(genre, session_id)
    response_results = response["results"]

    elements = []

    count = 0
    for result in response_results:
        if count < 10:

            buttons = [
                {
                    "type": "web_url",
                    "url": result["url"],
                    "title": "read story"
                }, {
                    "type": "postback",
                    "title": "Continue Chatting",
                    "payload": "ok"
                }
            ]

            element = {
                "title": result["title"],
                "image_url": result["multimedia"][3]["url"],
                "subtitle": result["abstract"],
                "default_action": {
                    "type": "web_url",
                    "url": result["url"],
                    "webview_height_ratio": "tall",
                },
                "buttons": buttons
            }

            elements.append(element)

            count += 1
        else:
            break

    return elements


if __name__ == '__main__':
    print(get_genre_templates("2750928681694983", "headlines", "test101"))
