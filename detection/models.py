from django.db import models
from accounts.models import Account

from django.db import models

class Detection(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)
    image_is_ai_generated = models.CharField(default=False,max_length=255)
    video_is_ai_generated = models.CharField(default=False,max_length=255)
    audio_is_ai_generated = models.CharField(default=False,max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    

    def _str_(self):
        return f"File: {self.file_path} - Image AI Generated: {self.image_is_ai_generated}, Video AI Generated: {self.video_is_ai_generated}, Audio AI Generated: {self.audio_is_ai_generated}"
