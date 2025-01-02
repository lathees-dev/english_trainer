import pymongo
from django.db import models
from django.contrib.auth.models import User

myClient=pymongo.MongoClient('mongodb://localhost:27017/')
class InterviewResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True)

class InterviewAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    rating = models.IntegerField()
    explanation = models.TextField()