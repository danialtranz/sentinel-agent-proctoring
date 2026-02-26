import os
import tempfile
from gtts import gTTS
import pygame
import threading
import time

class AlertSystem:
    def __init__(self, config):
        pygame.mixer.init()
        self.config = config
        self.alert_cooldown = config['logging']['alert_cooldown']
        self.last_alert_time = {}
        
        # Alert messages database
        self.alerts = {
            "FACE_DISAPPEARED": "Bạn hãy tập trung nhìn vào màn hình nha",
            "FACE_REAPPEARED": "Bạn đang tập trung rất tốt",
            "MULTIPLE_FACES": "Chúng tôi phát hiện có nhiều người trong khung hình",
            "OBJECT_DETECTED": "Vật thể không được phép được phát hiện trong khung hình",
            "GAZE_AWAY": "Bạn hãy tập trung nhìn vào màn hình nha",
            "MOUTH_MOVING": "Bạn hãy giữ im lặng trong khi thi",
            "SPEECH_VIOLATION": "Nói trong khi thi là không được phép",
            "VOICE_DETECTED": "Chúng tôi phát hiện giọng nói, bạn hãy giữ im lặng trong khi thi",
        }
        
    def _can_alert(self, alert_type):
        """Check if enough time has passed since last alert"""
        current_time = time.time()
        last_time = self.last_alert_time.get(alert_type, 0)
        return (current_time - last_time) >= self.alert_cooldown
        
    def speak_alert(self, alert_type):
        """Convert text to speech and play it"""
        if not self._can_alert(alert_type):
            return
            
        self.last_alert_time[alert_type] = time.time()
        
        def _play_audio():
            try:
                if alert_type in self.alerts:
                    # Generate speech
                    tts = gTTS(text=self.alerts[alert_type], lang='vi')
                    
                    # Save temporary audio file
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
                        temp_path = fp.name
                        tts.save(temp_path)
                    
                    # Play audio
                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()
                    
                    # Wait until playback finishes
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    
                    # Cleanup
                    os.unlink(temp_path)
            except Exception as e:
                print(f"Audio alert failed: {str(e)}")
        
        # Run in separate thread to avoid blocking
        threading.Thread(target=_play_audio, daemon=True).start()