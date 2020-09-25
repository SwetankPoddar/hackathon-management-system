from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

# User Model to include types
class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    USER_TYPE_CHOICES = (
      (1, 'team'),
      (2, 'judge'),
  )
    user_type = models.PositiveSmallIntegerField(choices = USER_TYPE_CHOICES, default = USER_TYPE_CHOICES[0][0], blank = True)

    def isAdmin(self):
        return self.user_type == 2

    def getType(self):
        if (self.user_type == 1):
            return "Team"
        else:
            return "Judge"

    def __str__(self):
        return str(self.user.id) + ' - ' + self.getType()

# Team Model
class Team(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length = 30)
    member_details = models.TextField(max_length = 350)
    hackerrank_accounts = models.TextField(max_length = 500)

    def __str__(self):
        return self.name



class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


# Challenge Model
class Challenge(models.Model):
    name = models.CharField(max_length = 50)
    points_avaliable = models.IntegerField()
    description = models.TextField(max_length = 350)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# Request Made Model (Includes the judgements made)
class RequestsMade(models.Model):

    # Team this request is related to
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    # Challenge this request is related to
    challenge = models.ForeignKey(Challenge, on_delete = models.CASCADE)

    points_gained = models.IntegerField(default=0, blank= True)

    REQUEST_STATUS = (
        ('request_made', 'Request made'),
        ('judged', 'Judged'),
    )

    status = models.CharField(max_length = 12,choices = REQUEST_STATUS, default = REQUEST_STATUS[0][0], blank = True)

    made_at = models.DateTimeField(default = datetime.now, blank = True)

    notes = models.TextField(default='', blank = True, max_length = 250 )

    closed_by = models.ForeignKey(CustomUser, on_delete = models.SET_NULL, blank = True, null = True )

    def __str__(self):
        team_name = str(self.team)
        question_name = str(self.challenge)
        time = str(self.made_at)
        return team_name +' - '+ question_name +' - '+ time
