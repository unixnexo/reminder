from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
  has_verified_email = models.BooleanField(default=False)


# class Reminder(models.Model):
#   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
#   reminder_text = models.TextField()
#   date_time = models.DateTimeField()
#   created_at = models.DateTimeField(auto_now_add=True)
#   thread_id = models.CharField(max_length=36, unique=True, null=True, blank=True)

class Reminder(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  message_thread_id = models.CharField(max_length=36, unique=True, null=True, blank=True)
  email_thread_id = models.CharField(max_length=36, unique=True, null=True, blank=True)
  discord_thread_id = models.CharField(max_length=36, unique=True, null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  reminder_text = models.TextField()
  date_time = models.DateTimeField()

  def __str__(self):
    return self.reminder_text


class UserSettings(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
  send_to_email = models.BooleanField(default=True)
  send_to_telegram = models.BooleanField(default=False)
  send_to_discord = models.BooleanField(default=False)
  telegram_id = models.CharField(max_length=20, blank=True, null=True)
  discord_id = models.CharField(max_length=100, blank=True, null=True)

  def __str__(self):
      return f"Settings for {self.user.username}"

# Signal to create user settings when a user is created
@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
  if created:
    UserSettings.objects.create(user=instance)
