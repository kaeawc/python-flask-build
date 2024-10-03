import logging
import logging.config
import yaml
import os

# Define the path to the logging configuration file
config_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "logging/logging_config.yml"
)


# Function to load YAML logging configuration
def setup_logging(config_path=config_path):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)


# Set up logging when this module is imported
setup_logging()

# Expose the root logger
logger = logging.getLogger()  # This grabs the default root logger
