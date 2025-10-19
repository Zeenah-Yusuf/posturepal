from datetime import datetime, timedelta

def stretch_reminder(last_stretch_time, interval_minutes=30):
    current_time = datetime.now()
    if current_time - last_stretch_time >= timedelta(minutes=interval_minutes):
        return True, current_time
    return False, last_stretch_time
