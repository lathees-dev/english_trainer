from django.db import models

class Question(models.Model):
    sentence = models.TextField()
    options = models.JSONField()  # To store multiple-choice options
    correct_answer = models.CharField(max_length=255)
