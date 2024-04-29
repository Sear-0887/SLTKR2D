def gettoken() -> str:
	try:
		from dotenv import dotenv_values
		token=dotenv_values("cred/client.env")['TOKEN']
		if token is None:
			raise Exception("No TOKEN.")
		return token
	except:
		raise Exception("Error on Loading TOKEN.")