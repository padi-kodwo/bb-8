# run the application
import logging as logger
import logging.config

import system_paths
from src import util
from server import app, serve

logger.config.fileConfig(system_paths.resource + "/config/logger.conf")


if __name__ == "__main__":
    server_type = "flask"
    host = util.get_property(property_section="serverSection", property_name="host.name")
    port = util.get_property(property_section="serverSection", property_name="host.port")

    if server_type is "flask":
        logger.info("about to launch app on " + server_type)
        app.run(debug=True, host=host, port=port)    # using the default
    elif server_type is "waitress":
        serve(app, host=host, port=port)