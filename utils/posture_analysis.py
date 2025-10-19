import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[1])
    angle = np.abs(radians * 180.0 / np.pi)
    return angle if angle <= 180 else 360 - angle

def analyze_posture(landmarks):
    feedback = []
    score = 100

    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    left_ear = [landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y]
    left_eye = [landmarks[mp_pose.PoseLandmark.LEFT_EYE.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_EYE.value].y]

    neck_angle = calculate_angle(left_shoulder, left_ear, left_eye)
    if neck_angle < 75:
        feedback.append("Tilt your head back – neck is leaning forward.")
        score -= 30

    left_y = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
    right_y = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y
    if abs(left_y - right_y) > 0.1:
        feedback.append("Level your shoulders – one is higher.")
        score -= 20

    return score, feedback
