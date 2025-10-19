import pandas as pd
import os
from utils.email_summary import send_weekly_summary
from utils.cloud_sync import upload_to_dropbox

user_db = "users.csv"
history_dir = "history"

users_df = pd.read_csv(user_db)
for _, row in users_df.iterrows():
    username = row["Username"]
    email = row.get("Email")
    if not email:
        continue

    history_file = f"{history_dir}/{username}_posture_log.xlsx"
    if os.path.exists(history_file):
        send_weekly_summary(username, email, history_file)
        upload_to_dropbox(history_file, f"/PosturePal/{username}_posture_log.xlsx")
        print(f"Sent summary and uploaded log for {username}")