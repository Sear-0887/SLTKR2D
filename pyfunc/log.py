import yaml
import logging
import os
from pyfunc.lang import cfg
from logging import config

def LoggerInit():
    os.makedirs(cfg('cacheFolder'), exist_ok=True) # directory to put images and other output in
    os.makedirs(cfg('logFolder'), exist_ok=True) # logs folder (may be in cache)
    with open(cfg('logConfigPath'), 'r', encoding = 'utf-8') as f:
        config = yaml.load(stream=f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)