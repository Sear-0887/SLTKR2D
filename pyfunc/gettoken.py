def gettoken() -> str:
	try:
		from dotenv import dotenv_values
		print("test")
		return dotenv_values("cred/client.env")['TOKEN']

	except:
		print("Error on Loading TOKEN.")