# G-Drive Dependencies
import os
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive"]


class GDrive:
    def __init__(self):
        self.u_creds = self.create_user_token()
        self.service = build("drive", "v3", credentials=self.u_creds)
        # self.u_credential_path = "../creds/token.json"

    def create_user_token(self) -> None:
        """
        Creates a user token. On first run, run locally to generate token.json and add to .secrets/
        """
        creds = None

        if os.path.exists("secrets/token.json"):
            creds = Credentials.from_authorized_user_file("secrets/token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "secrets/u_credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("secrets/token.json", "w") as token:
            token.write(creds.to_json())
        return creds

    def create_token(self) -> None:
        """
        Creates service token. Will be depreciated.
        """
        creds = None
        creds = service_account.Credentials.from_service_account_file(
            self.credential_path, scopes=SCOPES
        )
        return creds

    def list_files(self) -> None:
        """
        Lists all the files and folders in the root directory of g-drive.
        """
        try:
            results = (
                self.service.files()
                .list(pageSize=20, fields="nextPageToken, files(id, name)")
                .execute()
            )
            items = results.get("files", [])
            if not items:
                print("No files found.")
                return
            print("Files:")
            for item in items:
                print(f"{item['name']} ({item['id']})")
        except HttpError as error:
            print(f"An error occurred: {error}")

    def upload_files(self, file_paths: list[str], folder_id: str, del_f: bool = True):
        """
        Uploads files to the specified folder

        Parameters:
        file_paths: list[str], required
            List of file paths to be uploaded.
        folder_id: str, required
            Google drive folder ID to be uploaded into.
        del_f: bool, optional
            Boolean to specify deletion of file from local path after upload. True by default.

        Returns:
        None
        """
        # Uploads list of files in file_paths to folder_id
        for f_path in file_paths:
            try:
                # Create g-drive API client using desktop app and user credentials
                folder_path = "../Supplementary_data/DriveCredentials/{}".format(
                    folder_id
                )

                f_name = os.path.basename(f_path)
                file_metadata = {"name": f_name, "parents": [folder_id]}

                media = MediaFileUpload(
                    f_path, chunksize=10485760, resumable=True
                )  # 10MB chuncksize

                # pylint: disable=maybe-no-member
                file = (
                    self.service.files()
                    .create(body=file_metadata, media_body=media)
                    .execute()
                )
                print(
                    "\033[32m" + "{} UPLOADED SUCCESSFULLY".format(f_name) + "\033[0m"
                )

                # Delete from sandbox to save disc space
                if del_f:
                    os.remove(f_path)

            except HttpError as error:
                print(f"An error occurred: {error}")
                file = None
        return

    def delete_files(self, file_id: str) -> None:
        """
        Deletes the fileID or contents of folderID specified

        Parameters:
        file_id: str, required
            File or folder ID whose contents need to be deleted

        Returns:
        None
        """
        results = (
            self.service.files().list(q="'{}' in parents".format(file_id)).execute()
        )
        items = results.get("files", [])
        for item in items:
            try:
                response = self.service.files().delete(fileId=item["id"]).execute()
                print("FILE DELETED SUCCESSFULLY")
            except HttpError as error:
                print(f"An error occurred: {error}")

    def get_storage(self) -> pd.DataFrame:
        """
        Gets Google drive storage information.

        Returns:
        storage_df: pd.DataFrame
        """
        storage = self.service.about().get(fields="storageQuota").execute()
        print("Google Drive Storage")

        cap = int(storage["storageQuota"]["limit"]) / 10**9
        rem = (
            int(storage["storageQuota"]["limit"])
            - int(storage["storageQuota"]["usage"])
        ) / 10**9
        used = int(storage["storageQuota"]["usage"]) / 10**9
        used_d = int(storage["storageQuota"]["usageInDrive"]) / 10**9
        used_t = int(storage["storageQuota"]["usageInDriveTrash"]) / 10**9

        s_data = {
            "Loc": [
                "Capacity",
                "Available",
                "Usage",
                "Drive Usage",
                "Trash Usage",
            ],
            "Size in GB": [
                round(cap),
                round(rem),
                round(used),
                round(used_d),
                round(used_t),
            ],
        }
        storage_df = pd.DataFrame(s_data)
        storage_df.style.set_caption("Google Drive Storage")
        return storage_df
