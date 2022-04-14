from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from .engine import newboard


# Create your models here.
class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    opponent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opponent', null=True)
    owner_side= models.CharField(max_length=10, default="white")
    owner_online = models.BooleanField(default=False)
    opponent_online = models.BooleanField(default=False)
    boardstate = models.JSONField(default=newboard)
    winner = models.CharField(max_length=20, null=True, blank=True)
    level = models.CharField(max_length=15, null=True, blank=True)
    CHOICES=(
        (1,"Game Created"),
        (2,"Game Started"),
        (3,"Game Ended")
    )
    status = models.IntegerField(default=1,choices=CHOICES)
    whitemove = models.BooleanField(default=True)
    actioncount = models.IntegerField(default=0)
    white_captured = ArrayField(models.CharField(max_length=1, blank=True), size=10, null=True)
    black_captured = ArrayField(models.CharField(max_length=1, blank=True), size=10, null=True)