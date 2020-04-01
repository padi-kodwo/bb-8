import configparser
import logging as logger
import logging.config
import os
import uuid

import system_paths

# configure the logging format
logger.config.fileConfig(system_paths.resource + "/config/logger.conf")

config = configparser.RawConfigParser()
config.read(os.path.join(system_paths.resource, "config/local.properties"))


def get_property(property_section,property_name):
    if property_name is not None or property_section is not None:
        return config.get(property_section, property_name)
    else:
        return None


def session_id():
    return str(uuid.uuid1())


if __name__ == '__main__':
    print(get_property("serverSection", "host.address"))