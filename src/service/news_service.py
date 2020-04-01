import urllib.request

import logging as logger
import logging.config
import json
from newsapi import NewsApiClient

import system_paths
from src import util

# configure the logging format
logger.config.fileConfig(system_paths.resource + "/config/logger.conf")


def get_news_api_news(genre, session_id):
    logger.info("[ " + session_id + " ] about get news for genre " + genre)

    api_key = util.get_property("newsApiSection", "news.api.key")
    news_api = NewsApiClient(api_key=api_key)

    genre = None if "headlines" in genre.lower() else genre
    genre_query = genre

    if isinstance(genre, str) and "covid" in genre:
        genre_query = "coronavirus"

    top_headlines = news_api.get_top_headlines(q=genre_query,
                                               sources='bbc-news,the-verge,abc-news,al-jazeera-english,bloomberg,cnbc',
                                               category=None,
                                               language='en',
                                               country=None)

    logger.info("[ " + session_id + " ] done getting news for genre " + str(genre))

    return top_headlines

def get_nyt_news(genre, session_id):

    logger.info("[ " + session_id + " ] about get news for genre " + genre)
    news_api_genres_list = util.get_property(property_section="newsApiSection", property_name="news.api.genres.list").split(",")

    url = util.get_property("nytSection", "nyt.api.url." + genre.lower()) + "?api-key="
    url_request = urllib.request.urlopen(url + util.get_property("nytSection", "nyt.api.key"))

    json_response = json.loads(url_request.read())

    logger.info("[ " + session_id + " ] done getting nyt news for genre " + genre)

    return json_response


def get_science_news():
    url = util.get_property("nytSection", "nyt.api.url.science") + "?api-key="
    url_request = urllib.request.urlopen(url + util.get_property("nytSection", "nyt.api.key"))

    json_response = json.loads(url_request.read())

    print(json_response)
    return json_response


if __name__ == '__main__':
    print("i am here".replace(" ", ""))
    print(get_news_api_news("covid-19", "test101"))