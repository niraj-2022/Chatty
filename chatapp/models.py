from django.db import models
#from django.forms import CharField, TextField, ImageField


class ChatMsg(models.Model):
    msg_id = models.AutoField(primary_key=True)
    sender = models.CharField(max_length=50)
    receiver = models.CharField(max_length=50)
    message = models.TextField()


class Connections(models.Model):
    me = models.CharField(max_length=50)
    friend = models.CharField(max_length=50)
