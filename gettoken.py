def gettoken():
	try:
		from dotenv import dotenv_values
		print("test")
		return dotenv_values("cred/.env")['TOKEN']
		
	except:
		print("Error on Loading TOKEN.")