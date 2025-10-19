import streamlit as st
import os
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
import cv2
import mediapipe as mp
import pandas as pd
import time
from datetime import datetime, timedelta
from utils.posture_analysis import analyze_posture
from utils.viewer import render_model
from utils.voice import speak_feedback
from utils.reminders import stretch_reminder
import plotly.express as px
import random
import hashlib
import io
from dotenv import load_dotenv
load_dotenv()


# Initialize history_buffer
history_buffer = []

# --- Page Setup ---
st.set_page_config(page_title="PosturePal", layout="wide")

# --- Theme Toggle ---
theme = st.sidebar.radio("🌗 Theme", ["Dark", "Light"])

# --- Dynamic Styling ---
if theme == "Dark":
    bg_color = "#174D56FF"
    text_color = "#9CC7C5FF"
    sidebar_bg = "#174D56FF"
    sidebar_text = "#9CC7C5FF"
else:
    bg_color = "#9CC7C5FF"
    text_color = "#011013FF"
    sidebar_bg = "#70a3e2"
    sidebar_text = "#261B79"

st.write(f"Theme: {theme}, Background: {bg_color}, Text: {text_color}")

# --- Inject CSS ---
st.markdown(f"""
<style>
body {{
    background-color: {bg_color};
    font-family: 'Segoe UI', sans-serif;
}}

h1, h2, h3, h4, p, li {{
    color: {text_color};
}}

p, li {{
    font-size: 1rem;
    line-height: 1.6;
    color: {text_color};
}}

.sidebar .sidebar-content {{
    background-color: {sidebar_bg};
    color: {sidebar_text};
}}

#posture-score {{
    position: fixed;
    top: 20px;
    left: 20px;
    background: rgba(0,0,0,0.6);
    color: #3c6382;  /* Accent blue from logo arrow */
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 1.2rem;
    z-index: 100;
}}

.feedback-tip {{
    background: rgba(255,255,255,0.1);
    color: #ffcc00;
    padding: 8px;
    margin: 5px 0;
    border-radius: 6px;
    font-size: 0.95rem;
}}
</style>
""", unsafe_allow_html=True)

# --- Logo and Title ---
import os

logo_path = os.path.join("static", "posturepal_logo.jpg")

if os.path.exists(logo_path):
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image(logo_path, width=100)
    with col2:
        st.markdown(f"<h1 style='margin: 0; color: {text_color};'>PosturePal – Real-Time Posture Feedback</h1>", unsafe_allow_html=True)
else:
    st.title("🧍🏽‍♂️ PosturePal – Real-Time Posture Feedback")
    st.warning("Logo not found at 'static/posturepal_logo.jpg'. Please check the path.")

# --- Initialize Variables ---
# --- Multiuser Setup ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

user_db = "users.csv"
if not os.path.exists(user_db):
    pd.DataFrame(columns=["Username", "Password", "LastLogin"]).to_csv(user_db, index=False)

st.sidebar.header("👤 User Login")

# Load users
users_df = pd.read_csv(user_db)
user_list = users_df["Username"].tolist()

mode = st.sidebar.radio("Login Mode", ["Select User", "New User"])
if mode == "Select User":
    username = st.sidebar.selectbox("Choose Username", user_list)
    password = st.sidebar.text_input("Enter Password", type="password")
    user_row = users_df[users_df["Username"] == username]
    if not user_row.empty and hash_password(password) == user_row.iloc[0]["Password"]:
        st.sidebar.success(f"Welcome back, {username}!")
        users_df.loc[users_df["Username"] == username, "LastLogin"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        users_df.to_csv(user_db, index=False)
    else:
        st.warning("Invalid credentials.")
        st.stop()
elif mode == "New User":
    username = st.sidebar.text_input("Create Username")
    password = st.sidebar.text_input("Create Password", type="password")
    if st.sidebar.button("Register"):
        if username in user_list:
            st.warning("Username already exists.")
            st.stop()
        new_user = pd.DataFrame([[username, hash_password(password), datetime.now().strftime("%Y-%m-%d %H:%M:%S")]],
                                columns=["Username", "Password", "LastLogin"])
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        users_df.to_csv(user_db, index=False)
        st.sidebar.success(f"User {username} created. Please login.")
        st.stop()
    else:
        st.stop()

# --- User-Specific History File ---
history_dir = "history"
os.makedirs(history_dir, exist_ok=True)
history_file = f"{history_dir}/{username}_posture_log.xlsx"
if not os.path.exists(history_file):
    pd.DataFrame(columns=["Timestamp", "Score", "Feedback"]).to_excel(history_file, index=False)

# --- Profile Info ---
st.sidebar.subheader("👤 Profile Info")
last_login = users_df[users_df["Username"] == username]["LastLogin"].values[0]
st.sidebar.markdown(f"- **Username**: {username}")
st.sidebar.markdown(f"- **Last Login**: {last_login}")

# --- Password Reset ---
st.sidebar.subheader("🔑 Reset Password")
new_password = st.sidebar.text_input("New Password", type="password")
if st.sidebar.button("Update Password"):
    users_df.loc[users_df["Username"] == username, "Password"] = hash_password(new_password)
    users_df.to_csv(user_db, index=False)
    st.sidebar.success("Password updated.")

# --- Avatar Upload ---
avatar_dir = "avatars"
os.makedirs(avatar_dir, exist_ok=True)
avatar_path = f"{avatar_dir}/{username}.png"

st.sidebar.subheader("🖼️ Profile Avatar")
if os.path.exists(avatar_path):
    st.sidebar.image(avatar_path, width=80)
else:
    st.sidebar.info("No avatar uploaded.")

uploaded_avatar = st.sidebar.file_uploader("Upload Avatar", type=["png", "jpg", "jpeg"])
if uploaded_avatar:
    with open(avatar_path, "wb") as f:
        f.write(uploaded_avatar.getbuffer())
    st.sidebar.success("Avatar updated.")

# --- Admin Dashboard ---
if username == "admin":
    st.sidebar.subheader("🛠️ Admin Dashboard")
    all_users = pd.read_csv(user_db)
    selected_user = st.sidebar.selectbox("Manage User", all_users["Username"].tolist())
    
    if st.sidebar.button("Delete User"):
        all_users = all_users[all_users["Username"] != selected_user]
        all_users.to_csv(user_db, index=False)
        user_history = f"history/{selected_user}_posture_log.xlsx"
        user_avatar = f"avatars/{selected_user}.png"
        if os.path.exists(user_history): os.remove(user_history)
        if os.path.exists(user_avatar): os.remove(user_avatar)
        st.sidebar.success(f"User {selected_user} deleted.")
        st.stop()

    if st.sidebar.button("Reset User History"):
        pd.DataFrame(columns=["Timestamp", "Score", "Feedback"]).to_excel(f"history/{selected_user}_posture_log.xlsx", index=False)
        st.sidebar.success(f"{selected_user}'s history reset.")

# --- Webcam Toggle ---
run = st.sidebar.checkbox("Start Webcam")
FRAME_WINDOW = st.image([])

# --- History Setup ---
# Already defined earlier after login
history_file = f"history/{username}_posture_log.xlsx"
if not os.path.exists(history_file):
    pd.DataFrame(columns=["Timestamp", "Score", "Feedback"]).to_excel(history_file, index=False)
# --- Display Latest Posture Score with Animation ---
history_df = pd.read_excel(history_file)

# --- Display Latest Posture Score with Animation ---
if not history_df.empty:
    latest_score = history_df["Score"].iloc[-1]
    today = datetime.today().date()
    session_count = history_df[history_df["Date"].dt.date == today].shape[0]

    col1, col2 = st.columns([1, 3])  # Sidebar gets less space

    with col2:
        st.markdown("### 🧍‍♀️ Your Latest Posture Score")
        st.progress(int(latest_score))
        st.markdown(f"**Score: {latest_score}**")
        st.markdown(f"**Sessions Today:** {session_count}**")


    # --- Feedback Message Based on Score ---
    if latest_score >= 90:
        st.success("Excellent posture! Keep it up 💪")
    elif latest_score >= 70:
        st.warning("Good, but there's room to improve 🧘")
    else:
        st.error("Let's work on that posture! 🪑")

from utils.cloud_sync import upload_to_dropbox

upload_to_dropbox(history_file, f"/PosturePal/{username}_posture_log.xlsx")

# --- Avatar Pose Logic ---
def get_avatar_path(score):
    if score >= 80:
        return f"poses/standing_{random.choice([1, 2, 3])}.glb"
    elif 50 <= score < 80:
        return random.choice(["poses/sitting.glb", "poses/relaxing.glb"])
    else:
        return "poses/laying.glb"

# --- MediaPipe Setup ---
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

avatar_path = "poses/standing.glb"
if run:
    cap = cv2.VideoCapture(0)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                score, feedback = analyze_posture(results.pose_landmarks.landmark)
                avatar_path = get_avatar_path(score)

                st.markdown(f'<div id="posture-score">Posture Score: {score}</div>', unsafe_allow_html=True)
                for tip in feedback:
                    st.markdown(f'<div class="feedback-tip">💡 {tip}</div>', unsafe_allow_html=True)

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                history_buffer.append([timestamp, score, "; ".join(feedback)])

                if feedback:
                    speak_feedback(feedback)
                    for tip in feedback:
                        st.toast(f"🔔 {tip}", icon="💡")
                
                if "last_stretch_time" not in st.session_state:
                    st.session_state.last_stretch_time = datetime.now() - timedelta(minutes=30)

                should_remind, st.session_state.last_stretch_time = stretch_reminder(st.session_state.last_stretch_time)

                # should_remind, last_stretch_time = stretch_reminder(last_stretch_time)
                if should_remind:
                    st.toast("⏰ Time to stretch!", icon="🧘🏽‍♀️")
                    speak_feedback(["Time to stretch! You've been seated for a while."])

            FRAME_WINDOW.image(frame, channels="BGR")

        cap.release()

        # --- Save Buffered History After Webcam Session ---
        if history_buffer:
            try:
                df = pd.read_excel(history_file)
            except FileNotFoundError:
                df = pd.DataFrame(columns=["Timestamp", "Score", "Feedback"])

            new_df = pd.DataFrame(history_buffer, columns=["Timestamp", "Score", "Feedback"])
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_excel(history_file, index=False)

            history_buffer.clear()  # Reset buffer for next session


# # --- Save Buffered History ---
# if history_buffer:
#     df = pd.read_excel(history_file)
#     new_df = pd.DataFrame(history_buffer, columns=["Timestamp", "Score", "Feedback"])
#     df = pd.concat([df, new_df], ignore_index=True)
#     df.to_excel(history_file, index=False)

# --- Render Avatar ---
render_model(avatar_path)

# --- File Setup ---
history_file = "history/posture_log.xlsx"
os.makedirs("history", exist_ok=True)

# --- Log New Posture Entry ---
def log_posture(score, feedback):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = pd.DataFrame([{
        "Timestamp": timestamp,
        "Score": score,
        "Feedback": feedback
    }])

    try:
        existing_df = pd.read_excel(history_file)
    except FileNotFoundError:
        existing_df = pd.DataFrame(columns=["Timestamp", "Score", "Feedback"])

    updated_df = pd.concat([existing_df, new_entry], ignore_index=True)
    updated_df.to_excel(history_file, index=False)

    # --- Load History ---
try:
    history_df = pd.read_excel(history_file)
except FileNotFoundError:
    history_df = pd.DataFrame(columns=["Timestamp", "Score", "Feedback"])

# --- Clean and Format ---
history_df.columns = history_df.columns.str.strip()
history_df.rename(columns={"Timestamp": "Date"}, inplace=True)
history_df["Date"] = pd.to_datetime(history_df["Date"], errors="coerce")

st.sidebar.subheader("📅 Filter History")

min_date = history_df["Date"].min()
max_date = history_df["Date"].max()

# Fallback to today's date if min/max are NaT
fallback_date = datetime.today().date()
start_date = st.sidebar.date_input("Start", value=min_date.date() if pd.notna(min_date) else fallback_date)
end_date = st.sidebar.date_input("End", value=max_date.date() if pd.notna(max_date) else fallback_date)

filtered_df = history_df[
    (history_df["Date"].dt.date >= start_date) &
    (history_df["Date"].dt.date <= end_date)
]

if st.sidebar.button("🗑️ Reset History"):
    pd.DataFrame(columns=["Date", "Score", "Feedback"]).to_excel(history_file, index=False)
    st.success("Posture history has been reset.")
    st.stop()


st.subheader("📊 Posture History")
st.dataframe(filtered_df.tail(10))

# --- Download History as Excel ---
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    filtered_df.to_excel(writer, index=False)
excel_buffer.seek(0)

st.download_button(
    label="📥 Download History as Excel",
    data=excel_buffer,
    file_name="posture_history.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

today_df = filtered_df[filtered_df["Date"].dt.date == datetime.today().date()]
st.subheader("📅 Daily Posture Summary")
if not today_df.empty:
    avg_score = today_df["Score"].mean()
    session_count = len(today_df)
    all_feedback = "; ".join(today_df["Feedback"].dropna())
    feedback_list = [tip.strip() for tip in all_feedback.split(";") if tip.strip()]
    most_common_tip = max(set(feedback_list), key=feedback_list.count) if feedback_list else "None"

    st.markdown(f"""
    - **Average Score**: {avg_score:.1f}
    - **Sessions Today**: {session_count}
    - **Most Frequent Tip**: _{most_common_tip}_
    """)
else:
    st.info("No posture sessions logged today.")

def plot_and_export(df, x, y, title):
    fig = px.line(df, x=x, y=y, title=title)
    st.plotly_chart(fig, use_container_width=True)
    img_bytes = fig.to_image(format="png")
    st.download_button(f"📥 Export '{title}' as Image", data=img_bytes, file_name=f"{title}.png")

# Weekly Trend
weekly_df = filtered_df[filtered_df["Date"] >= pd.Timestamp.now() - pd.Timedelta(days=7)]
if not weekly_df.empty:
    weekly_avg = weekly_df.groupby("Date")["Score"].mean().reset_index()
    st.subheader("📈 Weekly Posture Trend")
    plot_and_export(weekly_avg, "Date", "Score", "Weekly Trend")

# Monthly Trend
monthly_df = filtered_df[filtered_df["Date"] >= pd.Timestamp.now() - pd.Timedelta(days=30)]
if not monthly_df.empty:
    monthly_avg = monthly_df.groupby("Date")["Score"].mean().reset_index()
    st.subheader("📅 Monthly Posture Trend")
    plot_and_export(monthly_avg, "Date", "Score", "Monthly Trend")

# Yearly Trend
yearly_df = filtered_df[filtered_df["Date"] >= pd.Timestamp.now() - pd.Timedelta(days=365)]
if not yearly_df.empty:
    yearly_df["Month"] = yearly_df["Date"].dt.to_period("M").astype(str)
    yearly_avg = yearly_df.groupby("Month")["Score"].mean().reset_index()
    st.subheader("📆 Yearly Posture Trend")
    plot_and_export(yearly_avg, "Month", "Score", "Yearly Trend")

score = 85
feedback = "Straighten your shoulders"
log_posture(score, feedback)

st.markdown("""
<style>
footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    text-align: center;
    font-size: 14px;
    color: gray;
    background-color: transparent;
}
</style>

<footer>
    Made with ❤️ by Zeenah Yusuf | PosturePal © 2025<br>
    <a href='mailto:support@posturepal.com'>Contact Support</a> | 
    <a href='https://posturepal.com/privacy' target='_blank'>Privacy Policy</a>
</footer>
""", unsafe_allow_html=True)
