import yaml
import logging
from pyfunc.lang import opencfg
from logging import config

def LoggerInit():
    with opencfg('logConfigPath', 'r', encoding = 'utf-8') as f:
        config = yaml.load(stream=f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)