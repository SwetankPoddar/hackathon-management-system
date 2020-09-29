from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
import os

class Organisation(models.Model):
    name = models.CharField(max_length = 60)

    def __str__(self):
        return self.name
class Judge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    organisation = models.ForeignKey(Organisation, on_delete=models.SET_NULL, null=True)

    def getType(self):
        return "judge"
    
    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' from ' + str(self.organisation)

# Team Model
class Team(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    name = models.CharField(max_length = 30)
    member_details = models.TextField(max_length = 350)
    hackerrank_accounts = models.TextField(max_length = 500)

    def getType(self):
        return "team"

    def __str__(self):
        return self.name + '(Team)'



class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=150, null=True)
    allowed_to_edit = models.ManyToManyField(Judge)
    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Attachments(models.Model):
    attachment =  models.FileField(upload_to='attachments/')
    def __str__(self):
        return os.path.basename(self.attachment.name)

# Challenge Model
class Challenge(models.Model):
    name = models.CharField(max_length = 50)
    points_avaliable = models.IntegerField()
    description = models.TextField(max_length = 350)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    attachments = models.ManyToManyField(Attachments)
    def __str__(self):
        return self.name

# Request Made Model (Includes the judgements made)
class RequestsMade(models.Model):

    # Team this request is related to
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    # Challenge this request is related to
    challenge = models.ForeignKey(Challenge, on_delete = models.CASCADE)

    points_gained = models.IntegerField(default=0, blank= True)

    attachments = models.ManyToManyField(Attachments)

    REQUEST_STATUS = (
        ('request_made', 'Request made'),
        ('judged', 'Judged'),
    )

    status = models.CharField(max_length = 12,choices = REQUEST_STATUS, default = REQUEST_STATUS[0][0], blank = True)

    made_at = models.DateTimeField(default = datetime.now, blank = True)

    notes = models.TextField(default='', blank = True, max_length = 250 )

    closed_by = models.ForeignKey(Judge, on_delete = models.SET_NULL, blank = True, null = True)

    def __str__(self):
        team_name = str(self.team)
        question_name = str(self.challenge)
        time = str(self.made_at)
        return team_name +' - '+ question_name +' - '+ time
