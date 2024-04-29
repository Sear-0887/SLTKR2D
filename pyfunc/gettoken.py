def gettoken():
	try:
		from dotenv import dotenv_values
		return dotenv_values("cred/client.env")['TOKEN']

	except:
		print("Error on Loading TOKEN.")