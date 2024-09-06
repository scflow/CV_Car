from loguru import logger
import yaml
import sys


def setlog():
    logger.remove()
    with open('loguru_config/loguru_config.yaml', 'r', encoding="utf-8") as file:
        config = yaml.safe_load(file)
    for handler_name, handler_config in config['handlers'].items():
        if handler_name == 'console':
            logger.add(sink=sys.stdout, level=handler_config['level'])
        elif handler_name == 'file':
            logger.add(sink=handler_config['sink'], level=handler_config['level'],
                       rotation=handler_config['rotation'], retention=handler_config['retention'])
