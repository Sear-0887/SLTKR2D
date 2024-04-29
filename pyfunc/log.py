import yaml
import logging
from pyfunc.lang import cfg
from logging import config

def LoggerInit():
    with open(cfg('logConfigPath'), 'r', encoding = 'utf-8') as f:
        config = yaml.load(stream=f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)