from django.db import models


class VideoFile(models.Model):
    video = models.FileField()
    video_data = models.BinaryField(null=True)

    def __str__(self):
        return self.video


class AudioFile(models.Model):
    audio_data = models.BinaryField()

    def __str__(self) -> str:
        return self.pk
