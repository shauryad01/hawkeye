import time
import cv2
import os
from datetime import datetime


class AlertManager:
    def __init__(self, risk_thresh=0.75, sustain_time=2.0, cooldown=10.0):
        self.risk_thresh = risk_thresh
        self.sustain_time = sustain_time
        self.cooldown = cooldown

        self.high_risk_start = None
        self.last_alert_time = 0.0

        os.makedirs("evidence", exist_ok=True)

    def update(self, frame, risk):
        now = time.time()

        # Check if risk is high
        if risk >= self.risk_thresh:
            if self.high_risk_start is None:
                self.high_risk_start = now
            elif now - self.high_risk_start >= self.sustain_time:
                if now - self.last_alert_time >= self.cooldown:
                    self.trigger_alert(frame, risk)
                    self.last_alert_time = now
                    self.high_risk_start = None
        else:
            self.high_risk_start = None

    def trigger_alert(self, frame, risk):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evidence/alert_{timestamp}_{int(risk*100)}.jpg"

        cv2.imwrite(filename, frame)
        print(f"ALERT TRIGGERED | Risk={int(risk*100)}% | Saved {filename}")
