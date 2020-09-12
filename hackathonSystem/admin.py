from django.contrib import admin
from .models import Challenge, RequestsMade, Team, CustomUser

# Register your models here.
admin.site.register(Challenge)
admin.site.register(RequestsMade)
admin.site.register(Team)
admin.site.register(CustomUser)
