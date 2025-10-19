from dotenv import load_dotenv
import os
import dropbox

load_dotenv()

dbx = dropbox.Dropbox(
    oauth2_refresh_token=os.getenv("DROPBOX_REFRESH_TOKEN"),
    app_key=os.getenv("DROPBOX_APP_KEY"),
    app_secret=os.getenv("DROPBOX_APP_SECRET")
)
def upload_to_dropbox(local_path, remote_path):
    with open(local_path, "rb") as f:
        dbx.files_upload(f.read(), remote_path, mode=dropbox.files.WriteMode.overwrite)
