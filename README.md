#  PosturePal

PosturePal is a real-time posture monitoring and feedback application built with Streamlit and MediaPipe. It uses your webcam to analyze your posture, provide corrective feedback, and track your progress over time. Whether you're working at a desk or practicing better ergonomics, PosturePal helps you sit and stand tall — one session at a time.


## Features

-  Real-time posture detection using your webcam
-  Posture scoring with animated feedback and improvement tips
-  Daily, weekly, monthly, and yearly posture trend tracking
-  Admin dashboard for managing users and resetting history
-  Dropbox integration for cloud-based history backup
-  3D avatar feedback that changes based on your posture
-  Smart stretch reminders to encourage healthy breaks


##  Project Structure


posturepal/
├── app.py                  # Main Streamlit app
├── utils/
│   └── cloud_sync.py       # Dropbox upload logic
├── poses/                  # 3D avatar models (.glb files)
├── avatars/                # User-uploaded profile pictures
├── history/                # User posture logs (Excel files)
├── .env                    # Environment variables (not tracked)
├── requirements.txt        # Python dependencies
└── .gitignore              # Files and folders to exclude from Git



## Installation

1. **Clone the repository**

bash
git clone https://github.com/yourusername/posturepal.git
cd posturepal


2. **Create and activate a virtual environment**

bash
python -m venv posturepal-env
# On Windows
posturepal-env\Scripts\activate
# On macOS/Linux
source posturepal-env/bin/activate


3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory with the following:

env
DROPBOX_APP_KEY=your_app_key
DROPBOX_APP_SECRET=your_app_secret
DROPBOX_REFRESH_TOKEN=your_refresh_token



##  Running the App

bash
streamlit run app.py


Then open the provided local URL in your browser to start using PosturePal.



## .gitignore Highlights

To keep your repository clean and secure, the following are excluded:

```gitignore
# Virtual environment
posturepal-env/

# Python cache
__pycache__/

# Streamlit cache and config
.streamlit/

# Secrets and credentials
.env
token.json
credentials.json

# User posture logs
history/
*.xlsx

# Avatar images and pose models
avatars/
poses/
*.png
*.jpg
*.jpeg
*.glb


**##  Admin Access**

To access the Admin Dashboard:

- Log in with the username: `admin`
- Manage users, delete accounts, or reset posture history


**##  Dropbox Integration**

PosturePal automatically uploads user posture logs to Dropbox using the Dropbox API. Ensure your `.env` file contains valid credentials and a refresh token.


**## Future Enhancements**

- Google Drive sync option
- Session-based analytics and summaries
- Email reports and reminders
- Mobile-friendly UI
- AI-based posture correction suggestions


**##  Contributing**

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request



**##  Questions or Feedback?**

Feel free to open an issue or reach out with suggestions. Let’s build better posture habits together!
