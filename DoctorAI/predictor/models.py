from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    middle_name = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField()
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username

class GenomeUpload(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    genome_file = models.FileField(upload_to='genomes/')
    symptoms = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.uploaded_at}"

from django.conf import settings  # Import settings

class PredictionResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    result_file = models.FileField(upload_to='results/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Result {self.id} - {self.user.username}'
