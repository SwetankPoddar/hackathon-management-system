from django.contrib import admin
from .models import Challenge, RequestsMade, Team, Organisation, Judge, Category, Attachments

# Register your models here.
admin.site.register(Challenge)
admin.site.register(RequestsMade)
admin.site.register(Team)
admin.site.register(Organisation)
admin.site.register(Judge)
admin.site.register(Category)
admin.site.register(Attachments)
