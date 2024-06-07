import yaml
import logging
import os
from pyfunc.lang import opencfg, cfg
import logging.config

def LoggerInit() -> None:
    os.makedirs(cfg('cacheFolder'), exist_ok=True) # directory to put images and other output in
    os.makedirs(cfg('logFolder'), exist_ok=True) # logs folder (may be in cache)
    with opencfg('logConfigPath', 'r') as f:
        config = yaml.load(stream=f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)