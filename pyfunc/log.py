import yaml
import logging
import os
from pyfunc.lang import opencfg, cfgstr
import logging.config

def LoggerInit() -> None:
    os.makedirs(cfgstr('cacheFolder'), exist_ok=True) # directory to put images and other output in
    os.makedirs(cfgstr('logFolder'), exist_ok=True) # logs folder (may be in cache)
    with opencfg('logConfigPath', 'r', encoding = 'utf-8') as f:
        config = yaml.load(stream=f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)