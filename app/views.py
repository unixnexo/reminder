from django.http import HttpRequest, HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .models import User
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login
from .services import send_sign_in_email, decode_uid, get_user_by_uid
from .forms import CreateUserForm
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .scheduler import cancel_scheduled_message, cancel_scheduled_email, schedule_message, schedule_email, schedule_discord_message, cancel_scheduled_discord_message
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseBadRequest
import time
from django.conf import settings

from .models import Reminder, User, UserSettings


### Verify user email after the user clicks on the email link ###
def verify_email(request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
    uid = decode_uid(uidb64)
    user = get_user_by_uid(uid) if uid else None

    if user and default_token_generator.check_token(user, token):
        user.has_verified_email = True
        user.save()
        login(request, user)
        return redirect('home')

    print("Email verification failed")
    return redirect('auth')


class SendSignInEmail(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_anonymous and request.user.has_verified_email:
            return redirect('home')
        form = CreateUserForm()
        return render(request, 'auth.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        data = {
            'username': request.POST['email'],
            'email': request.POST['email'],
            'password': request.POST['email']
        }
        user, created = User.objects.get_or_create(
            email=data['email'],
            defaults={'username': data['email'], 'password': data['email']}
        )
        return self._send_verification_and_respond(user)

    @staticmethod
    def _send_verification_and_respond(user: User) -> HttpResponse:
        send_sign_in_email(user)
        message = (
            f"Check your email, "
            f'<a href=mailto:{user.email}" target="_blank">{user.email}</a>'
            ", to verify and login."
        )
        return HttpResponse(message)


@login_required
def sign_out(request: HttpRequest) -> HttpResponse:
  request.session.flush()
  return redirect('auth')


def home(request: HttpRequest) -> HttpResponse:
    if not request.user.is_anonymous and request.user.has_verified_email:
        reminders = Reminder.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'main.html', {'reminders': reminders})
    else:
        return redirect('auth')


def user_settings(request: HttpRequest) -> HttpResponse:
    if not request.user.is_anonymous and request.user.has_verified_email:
        user_settings = UserSettings.objects.get(user=request.user)
        userEmail = User.objects.get(username=request.user.username).email
        telegram_id = user_settings.telegram_id
        discord_id = user_settings.discord_id

        return render(request, 'settings.html', {'user_email': userEmail, 'telegram_id': telegram_id, 'discord_id': discord_id, 'send_to_email': user_settings.send_to_email, 'send_to_telegram': user_settings.send_to_telegram, 'send_to_discord': user_settings.send_to_discord})
    else:
        return redirect('auth')


# @login_required
# def add_reminder(request):
#     if request.method == 'POST':
#         reminder_text = request.POST.get('text')
#         date_time_str = request.POST.get('dateTime')
#         user = request.user

#         if reminder_text and date_time_str:
#             date_time = timezone.datetime.fromisoformat(date_time_str)
#             reminder = Reminder.objects.create(
#                 user=user,
#                 reminder_text=reminder_text,
#                 date_time=date_time
#             )

#             try:
#                 user_settings = UserSettings.objects.get(user=user)

#                 # Send to Telegram if enabled
#                 if user_settings.send_to_telegram and user_settings.telegram_id:
#                     chat_id = user_settings.telegram_id
#                     thread_id = schedule_message(chat_id, reminder_text, date_time.timestamp())
#                     reminder.thread_id = thread_id
#                     reminder.save()

#                 # Send to Email if enabled
#                 if user_settings.send_to_email:
#                     subject = 'Reminder Notification 🔴💬'
#                     message = (
#                         '<div style="background-color:#1D232A;color:white;height:50vh;padding:20px;border-radius:20px;font-size:25px;text-align:center;">'
#                         '🌎 This is from riminder.pythonanywhere.com 🌎<br/>'
#                         f'<h1>{reminder_text}</h1>'
#                         '</div>'
#                     )
#                     from_email = settings.EMAIL_HOST_USER
#                     recipient_list = [user.email]
#                     thread_id = schedule_email(subject, message, from_email, recipient_list, date_time.timestamp())
#                     reminder.thread_id = thread_id
#                     reminder.save()

#                 # Send to Discord if enabled
#                 if user_settings.send_to_discord and user_settings.discord_id:
#                     channel_id = user_settings.discord_id
#                     thread_id = schedule_discord_message(channel_id, reminder_text, date_time.timestamp())
#                     reminder.thread_id = thread_id
#                     reminder.save()

#             except UserSettings.DoesNotExist:
#                 return JsonResponse({'error': 'User settings not found'}, status=404)

#             response = JsonResponse({'message': 'Reminder added successfully!'})
#             response['HX-Trigger'] = 'fire' # send custom header to refresh the reminders
#             return response
#         else:
#             return JsonResponse({'error': 'Invalid input'}, status=400)

#     return JsonResponse({'error': 'Invalid request method'}, status=405)


# @login_required
# def delete_reminder(request, reminder_id):
#     reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)

#     if request.method == 'POST':
#         thread_id = reminder.thread_id
#         if thread_id:
#             cancel_scheduled_message(thread_id)
#             cancel_scheduled_email(thread_id)
#             cancel_scheduled_discord_message(thread_id)

#         reminder.delete()
#         return HttpResponse(status=200) # so nothing will show up in the DOM

#     return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def refresh_reminders(request):
    reminders = Reminder.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'partials/reminder.html', {'reminders': reminders})


@login_required
def toggle_send_to_email(request):
    try:
        user_settings = get_object_or_404(UserSettings, user=request.user)
        
        user_settings.send_to_email = not user_settings.send_to_email
        user_settings.save()
        
        if user_settings.send_to_email:
            message = "Enabled"
        else:
            message = "Disabled"
        
        return HttpResponse(message, status=200)
    
    except UserSettings.DoesNotExist:
        return HttpResponse("User settings not found", status=404)
    except Exception as e:
        return HttpResponseBadRequest("Error: " + str(e))


@login_required
def toggle_send_to_telegram(request):
    try:
        user_settings = get_object_or_404(UserSettings, user=request.user)
        
        telegram_id = request.POST.get('telegram_id') 

        if telegram_id:
            user_settings.send_to_telegram = not user_settings.send_to_telegram
            
            if user_settings.send_to_telegram:
                user_settings.telegram_id = telegram_id
            else:
                user_settings.telegram_id = None
            
            user_settings.save()

            if user_settings.send_to_telegram:
                message = "Enabled"
            else:
                message = "Disabled"

            return HttpResponse(message, status=200)
        else:
            return HttpResponseBadRequest("Telegram ID is required")

    except UserSettings.DoesNotExist:
        return HttpResponse("User settings not found", status=404)
    except Exception as e:
        return HttpResponseBadRequest("Error: " + str(e))


@login_required
def toggle_send_to_discord(request):
    try:
        user_settings = get_object_or_404(UserSettings, user=request.user)
        
        discord_id = request.POST.get('discord_id') 

        if discord_id:
            user_settings.send_to_discord = not user_settings.send_to_discord
            
            if user_settings.send_to_discord:
                user_settings.discord_id = discord_id
            else:
                user_settings.discord_id = None
            
            user_settings.save()

            if user_settings.send_to_discord:
                message = "Enabled"
            else:
                message = "Disabled"

            return HttpResponse(message, status=200)
        else:
            return HttpResponseBadRequest("Discord Channel ID is required")

    except UserSettings.DoesNotExist:
        return HttpResponse("User settings not found", status=404)
    except Exception as e:
        return HttpResponseBadRequest("Error: " + str(e))


######## test ########
@login_required
def delete_reminder(request, reminder_id):
  reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)

  if request.method == 'POST':
    # Attempt to cancel each type of scheduled task
    if reminder.message_thread_id:
      cancel_scheduled_message(reminder.message_thread_id)
    if reminder.email_thread_id:
      cancel_scheduled_email(reminder.email_thread_id)
    if reminder.discord_thread_id:
      cancel_scheduled_discord_message(reminder.discord_thread_id)

    reminder.delete()
    return HttpResponse(status=200)  # so nothing will show up in the DOM

  return JsonResponse({'error': 'Invalid request method'}, status=405)



@login_required
def add_reminder(request):
  if request.method == 'POST':
    reminder_text = request.POST.get('text')
    date_time_str = request.POST.get('dateTime')
    user = request.user

    if reminder_text and date_time_str:
      date_time = timezone.datetime.fromisoformat(date_time_str)
      reminder = Reminder.objects.create(
        user=user,
        reminder_text=reminder_text,
        date_time=date_time
      )

      try:
        user_settings = UserSettings.objects.get(user=user)

        # Send to Telegram if enabled
        if user_settings.send_to_telegram and user_settings.telegram_id:
          chat_id = user_settings.telegram_id
          thread_id = schedule_message(chat_id, reminder_text, date_time.timestamp())
          reminder.message_thread_id = thread_id

        # Send to Email if enabled
        if user_settings.send_to_email:
          subject = 'Reminder Notification 🔴💬'
          message = (
            '<div style="background-color:#1D232A;color:white;height:50vh;padding:20px;border-radius:20px;font-size:25px;text-align:center;">'
            '🌎 This is from riminder.pythonanywhere.com 🌎<br/>'
            f'<h1>{reminder_text}</h1>'
            '</div>'
          )
          from_email = settings.EMAIL_HOST_USER
          recipient_list = [user.email]
          thread_id = schedule_email(subject, message, from_email, recipient_list, date_time.timestamp())
          reminder.email_thread_id = thread_id

        # Send to Discord if enabled
        if user_settings.send_to_discord and user_settings.discord_id:
          channel_id = user_settings.discord_id
          thread_id = schedule_discord_message(channel_id, reminder_text, date_time.timestamp())
          reminder.discord_thread_id = thread_id

        # Save the updated reminder with thread IDs
        reminder.save()

      except UserSettings.DoesNotExist:
        return JsonResponse({'error': 'User settings not found'}, status=404)

      response = JsonResponse({'message': 'Reminder added successfully!'})
      response['HX-Trigger'] = 'fire' # send custom header to refresh the reminders
      return response
    else:
      return JsonResponse({'error': 'Invalid input'}, status=400)

  return JsonResponse({'error': 'Invalid request method'}, status=405)










'''
ALPHA
'''
### WORKS WITH OUT TERMINATION ###
# @login_required
# def add_reminder(request):
#   if request.method == 'POST':
#     reminder_text = request.POST.get('text')
#     date_time_str = request.POST.get('dateTime')
#     user = request.user

#     if reminder_text and date_time_str:
#       date_time = timezone.datetime.fromisoformat(date_time_str)
#       Reminder.objects.create(
#         user=user,
#         reminder_text=reminder_text,
#         date_time=date_time
#       )

#       ## send reminders on different apps
#       try:
#         user_settings = UserSettings.objects.get(user=user)
        
#         # Send to Telegram if enabled
#         if user_settings.send_to_telegram and user_settings.telegram_id:
#           chat_id = user_settings.telegram_id
#           schedule_message(chat_id, reminder_text, date_time.timestamp())

#         # Send to Email if enabled
#         if user_settings.send_to_email:
#           subject = 'Reminder Notification 🔴💬'
#           message = (
#             '<div style="background-color:#1D232A;color:white;height:50vh;padding:20px;border-radius:20px;font-size:25px;text-align:center;">'
#             '🌎 This is from riminder.pythonanywhere.com 🌎<br/>'
#             f'<h1>{reminder_text}</h1>'
#             '</div>'
#           )
#           from_email = settings.EMAIL_HOST_USER
#           recipient_list = [user.email]
#           schedule_email(subject, message, from_email, recipient_list, date_time.timestamp())

#       except UserSettings.DoesNotExist:
#         return JsonResponse({'error': 'User settings not found'}, status=404)

#       response = JsonResponse({'message': 'Reminder added successfully!'})
#       response['HX-Trigger'] = 'fire' # send custom header to refresh the reminders
#       return response
#     else:
#       return JsonResponse({'error': 'Invalid input'}, status=400)

#   return JsonResponse({'error': 'Invalid request method'}, status=405)


# @login_required
# def delete_reminder(request, reminder_id):
#   reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)

#   if request.method == 'POST':
#     reminder.delete()
#     return HttpResponse(status=200) # so nothing will show up in the DOM

#   return JsonResponse({'error': 'Invalid request method'}, status=405)
