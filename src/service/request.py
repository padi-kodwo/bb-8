import logging as logger
import logging.config
import os

import dialogflow
from google.api_core.exceptions import InvalidArgument

import system_paths

# configure the logging format
logger.config.fileConfig(system_paths.resource + "/config/logger.conf")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Pools-Agent-12-ae9f87bbd9b2.json"
DIALOGFLOW_PROJECT_ID = 'pools-agent-12'
DIALOGFLOW_LANGUAGE_CODE = 'en'
SESSION_ID = 'me'


class Dialogflow:
    def __init__(self, text):
        self.session_client = dialogflow.SessionsClient()
        self.session = self.session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
        self.text = text
        pass

    def get_kb_response(self):
        logger.info("about to get query response")
        text_input = dialogflow.types.TextInput(text=self.text, language_code=DIALOGFLOW_LANGUAGE_CODE)
        query = dialogflow.types.QueryInput(text=text_input)

        try:
            response = self.session_client.detect_intent(session=self.session, query_input=query)
            logger.info("done getting response from dialog flow: " + str(response))
            return response
        except InvalidArgument as e:
            print(f"something went wrong {e}")
            pass
        pass
    pass


def _call_(text):
    dialogflow = Dialogflow(text)
    response = dialogflow.get_kb_response()
    print(response)


if __name__ == '__main__':
    _call_("Hi")