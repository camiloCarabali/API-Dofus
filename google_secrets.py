from google.cloud import secretmanager

secret_client = secretmanager.SecretManagerServiceClient()


def get_secret(secret_name):
    name = f"projects/587329480000/secrets/{secret_name}/versions/latest"
    response = secret_client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")


username = get_secret("USERNAME_MONGODB")
password = get_secret("PASSWORD_MONGODB")

connection_string = f"mongodb+srv://{username}:{password}@dofusquest.j66xz.mongodb.net/"
