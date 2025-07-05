import os

from azure.storage.blob import BlobServiceClient


class AzureBlobStorage:
    def __init__(self):
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        self._create_container_if_not_exists()

    def _create_container_if_not_exists(self):
        try:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            container_client.create_container(public_access="container")
            print(f"Container '{self.container_name}' created.")
        except Exception:
            # Container likely already exists
            pass

    def upload_file(self, file_name, file_content):
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=file_name
        )
        blob_client.upload_blob(file_content, overwrite=True)
        return blob_client.url.replace("swvista-azurite", "localhost")
