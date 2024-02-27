import config
import os

def gettoken():
	errs=[]
	try:
		# dotenv file
		from dotenv import dotenv_values
		return dotenv_values(os.path.join(config.creddir,".env"))['TOKEN']
	except Exception as e:
		errs.append(e)
	try:
		# token in cred/
		with open(os.path.join(config.creddir,"token")) as f:
			token=f.read()
		return token
	except Exception as e:
		errs.append(e)
	try:
		# token in main directory
		with open("token") as f:
			token=f.read()
		return token
	except Exception as e:
		errs.append(e)
	try:
		# token in environment
		return os.environ['token']
	except Exception as e:
		errs.append(e)
	raise Exception("Error on Loading TOKEN.",errs)

token=gettoken()