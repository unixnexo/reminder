from django.contrib import admin
from .models import User, Reminder, UserSettings

admin.site.register(User)
admin.site.register(Reminder)
admin.site.register(UserSettings)
