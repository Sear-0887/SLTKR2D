import logging


l = logging.getLogger()

def getclientenv(key: str) -> str:
	# try:
		from pyfunc.lang import cfg
		from dotenv import dotenv_values
		value = dotenv_values(cfg("TOKENPATH"))
		if key not in value.keys():
			l.error(f"Unable to fetch {key} from {cfg('TOKENPATH')}. Returned None.")
			return None
		value = value[key]
		return value
	# except:
	# 	raise Exception("Error on Loading TOKEN.")