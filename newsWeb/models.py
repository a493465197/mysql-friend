from email.policy import default
from django.db import models
from datetime import datetime
import random


class users(models.Model):
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    isAdmin = models.BooleanField(max_length=200, default=False)
    genre = models.IntegerField(max_length=200, default= 0)
    age = models.IntegerField(max_length=200, default= 20)
    like_movies = models.CharField(max_length=200)
    like_movies_title = models.CharField(max_length=200, default= '')
    like_age = models.CharField(max_length=200)
    time = models.CharField(max_length=200, default= '')

class movies(models.Model):
    title = models.CharField(max_length=200, primary_key=True)
    description = models.CharField(max_length=200)
    director = models.CharField(max_length=200)
    topCast = models.CharField(max_length=200)
    year = models.IntegerField(default= 2000)
    genre = models.CharField(max_length=200)
    actor = models.CharField(max_length=200)
    poster = models.CharField(max_length=200)
    date = models.CharField(max_length=200, default= '')
    rating = models.CharField(max_length=200, default= '')
    time = models.CharField(max_length=200, default= '')

class rating(models.Model):
    title = models.CharField(max_length=200)
    rating = models.IntegerField(default= 10)
    username = models.CharField(max_length=200)


class push(models.Model):
    username = models.CharField(max_length=200)
    pusername = models.CharField(max_length=200)
    time = models.CharField(max_length=200, default= '')
