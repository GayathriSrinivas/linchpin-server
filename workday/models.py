from django.db import models

# Create your models here.
class Message(models.Model):
    sender = models.CharField(max_length=200)
    receiver = models.CharField(max_length=200)
    msg = models.CharField(max_length=500)

    def __unicode__(self):  
    	return self.sender + "::" + self.receiver + "::" + self.msg

class User(models.Model):
    username = models.CharField(max_length=200, primary_key=True)
    password = models.CharField(max_length=200)
    gcmId = models.CharField(max_length=5000)
    picture = models.CharField(max_length=20)

    def __unicode__(self):  
    	return self.username + "::" + self.password + "::" + self.picture + "::" + self.gcmId
