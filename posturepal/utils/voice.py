import pyttsx3

def speak_feedback(feedback_list):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    for feedback in feedback_list:
        engine.say(feedback)
    engine.runAndWait()
