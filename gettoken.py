def gettoken():
	try:
		from dotenv import dotenv_values
		dotenv_values("cred/.env")['TOKEN']
	except:
		pass
	try:
		with open('creds/token') as f:
			token=f.read()
		return token
	except:
		pass
	try:
		import os
		return os.environ['token']
	except:
		pass