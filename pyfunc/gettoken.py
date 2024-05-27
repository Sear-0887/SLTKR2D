import logging


l = logging.getLogger()

def getclientenv(key: str) -> str | None:
	# try:
		from pyfunc.lang import cfgstr
		from dotenv import dotenv_values
		value = dotenv_values(cfgstr("TOKENPATH"))
		return value.get(key)
	# except:
	# 	raise Exception("Error on Loading TOKEN.")