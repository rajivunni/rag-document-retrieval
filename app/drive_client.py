from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def build_drive_service(service_account_file: str):
    credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
    return build("drive", "v3", credentials=credentials)


def list_files(service, folder_id: str) -> list[dict]:
    response = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, mimeType, modifiedTime)",
    ).execute()
    return response.get("files", [])


def download_file(service, file_id: str) -> bytes:
    return service.files().get_media(fileId=file_id).execute()
