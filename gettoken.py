import config

def gettoken():
	try:
		from dotenv import dotenv_values
		print("test")
		return dotenv_values(os.path.join(config.creddir,".env"))['TOKEN']
	except:
		pass
	try:
		with open(os.path.join(config.creddir,"token")) as f:
			token=f.read()
		return token
	except:
		pass
	try:
		import os
		return os.environ['token']
	except:
		print("Error on Loading TOKEN.")

token=gettoken()