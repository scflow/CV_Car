import logging.config
import logging
import yaml


def set_logging():
    with open("./log/log_config.yaml", 'r') as file:
        config_yaml = yaml.safe_load(file)
        logging.config.dictConfig(config=config_yaml)
