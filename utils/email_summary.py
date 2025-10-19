import smtplib
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st

def send_weekly_summary(username, email, history_file):
    df = pd.read_excel(history_file)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    last_week = df[df["Timestamp"] >= pd.Timestamp.now() - pd.Timedelta(days=7)]

    avg_score = last_week["Score"].mean()
    tips = "; ".join(last_week["Feedback"].dropna())
    summary = f"Hi {username},\n\nYour average posture score this week was {avg_score:.1f}.\nTop tips: {tips}"

    msg = MIMEText(summary)
    msg["Subject"] = "Your Weekly Posture Summary"
    msg["From"] = st.secrets["EMAIL_USERNAME"]
    msg["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(st.secrets["EMAIL_USERNAME"], st.secrets["EMAIL_PASSWORD"])
        server.send_message(msg)
    st.success("Weekly summary email sent!")