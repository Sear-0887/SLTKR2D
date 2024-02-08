def gettoken():
	try:
		from dotenv import dotenv_values
		dotenv_values("cred/.env")['TOKEN']
	except:
		with open('creds/token') as f
			token=f.read()
		return token