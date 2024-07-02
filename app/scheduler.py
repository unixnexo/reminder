### WORKS BUT NOT TERMINATION ###
# import time
# import requests
# import threading
# from django.core.mail import send_mail
# from django.conf import settings

# ##
# # Telegram
# ##
# bot_token = '7236178087:AAFw_is-lqDzLNiHn5aI57PwE1BV5XM0FxI'

# def send_scheduled_message(chat_id, text, schedule_timestamp):
#     delay = schedule_timestamp - time.time()
    
#     if delay > 0:
#         time.sleep(delay)

#     # directly from telegram api
#     # url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
#     # params = {'chat_id': chat_id, 'text': text}
#     # response = requests.get(url, params=params)

#     url = f'https://reminderworker.ali-unix-24.workers.dev/?token={bot_token}&text={text}&id={chat_id}'
#     response = requests.get(url)

    
#     if response.status_code == 200:
#         print(f'Message sent successfully to {chat_id}')
#     else:
#         print(f'Failed to send message to {chat_id}')

# def schedule_message(chat_id, text, schedule_timestamp):
#     thread = threading.Thread(target=send_scheduled_message, args=(chat_id, text, schedule_timestamp))
#     thread.start()


# ##
# # Email
# ##
# def send_scheduled_email(subject, message, from_email, recipient_list, schedule_timestamp):
#   delay = schedule_timestamp - time.time()
  
#   if delay > 0:
#     time.sleep(delay)
  
#   send_mail(subject, message, from_email, recipient_list, html_message=message)

# def schedule_email(subject, message, from_email, recipient_list, schedule_timestamp):
#   thread = threading.Thread(target=send_scheduled_email, args=(subject, message, from_email, recipient_list, schedule_timestamp))
#   thread.start()



### WORKS WITH TERMINATION ### PROBLEM with cancellation all
# import time
# import requests
# import threading
# import uuid
# from django.conf import settings
# from django.core.mail import send_mail

# # Track threads and their stop events
# scheduled_threads = {}
# thread_stop_events = {}

# # Telegram
# bot_token = settings.BOT_TOKEN

# def send_scheduled_message(chat_id, text, schedule_timestamp, stop_event):
#     delay = schedule_timestamp - time.time()
#     if delay > 0 and not stop_event.wait(timeout=delay):
#         url = f'https://reminderworker.ali-unix-24.workers.dev/?token={bot_token}&text={text}&id={chat_id}'
#         response = requests.get(url)

#         if response.status_code == 200:
#             print(f'Message sent successfully to {chat_id}')
#         else:
#             print(f'Failed to send message to {chat_id}')

# def schedule_message(chat_id, text, schedule_timestamp):
#     stop_event = threading.Event()
#     thread = threading.Thread(target=send_scheduled_message, args=(chat_id, text, schedule_timestamp, stop_event))
#     thread_id = str(uuid.uuid4())
#     scheduled_threads[thread_id] = thread
#     thread_stop_events[thread_id] = stop_event
#     thread.start()
#     return thread_id

# def cancel_scheduled_message(thread_id):
#     if thread_id in thread_stop_events:
#         thread_stop_events[thread_id].set()
#         return True
#     return False


# # Email
# def send_scheduled_email(subject, message, from_email, recipient_list, schedule_timestamp, stop_event):
#     delay = schedule_timestamp - time.time()
#     if delay > 0 and not stop_event.wait(timeout=delay):
#         send_mail(subject, message, from_email, recipient_list, html_message=message)

# def schedule_email(subject, message, from_email, recipient_list, schedule_timestamp):
#     stop_event = threading.Event()
#     thread = threading.Thread(target=send_scheduled_email, args=(subject, message, from_email, recipient_list, schedule_timestamp, stop_event))
#     thread_id = str(uuid.uuid4())
#     scheduled_threads[thread_id] = thread
#     thread_stop_events[thread_id] = stop_event
#     thread.start()
#     return thread_id

# def cancel_scheduled_email(thread_id):
#     if thread_id in thread_stop_events:
#         thread_stop_events[thread_id].set()
#         return True
#     return False


# # Discord
# Authorization = settings.AUTHORIZATION

# def send_scheduled_discord_message(channel_id, content, schedule_timestamp, stop_event):
#     delay = schedule_timestamp - time.time()
#     if delay > 0 and not stop_event.wait(timeout=delay):
#         url = f'https://discord.com/api/v9/channels/{channel_id}/messages'
#         payload = {"content": content}
#         headers = {"Authorization": Authorization}

#         response = requests.post(url, json=payload, headers=headers)

#         if response.status_code == 200:
#             print(f'Message sent successfully to channel {channel_id}')
#         else:
#             print(f'Failed to send message to channel {channel_id}')

# def schedule_discord_message(channel_id, content, schedule_timestamp):
#     stop_event = threading.Event()
#     thread = threading.Thread(target=send_scheduled_discord_message, args=(channel_id, content, schedule_timestamp, stop_event))
#     thread_id = str(uuid.uuid4())
#     scheduled_threads[thread_id] = thread
#     thread_stop_events[thread_id] = stop_event
#     thread.start()
#     return thread_id

# def cancel_scheduled_discord_message(thread_id):
#     if thread_id in thread_stop_events:
#         thread_stop_events[thread_id].set()
#         return True
#     return False




### TEST ###
import uuid
import time
import threading
import requests
from django.conf import settings
from django.core.mail import send_mail

# Track threads and their stop events
scheduled_threads = {}
thread_stop_events = {}

# Telegram
bot_token = settings.BOT_TOKEN

def send_scheduled_message(chat_id, text, schedule_timestamp, stop_event):
  delay = schedule_timestamp - time.time()
  if delay > 0 and not stop_event.wait(timeout=delay):
    url = f'https://reminderworker.ali-unix-24.workers.dev/?token={bot_token}&text={text}&id={chat_id}'
    response = requests.get(url)
    if response.status_code == 200:
      print(f'Message sent successfully to {chat_id}')
    else:
      print(f'Failed to send message to {chat_id}')
  else:
    print(f"Message to {chat_id} cancelled or already executed.")

def schedule_message(chat_id, text, schedule_timestamp):
  stop_event = threading.Event()
  thread = threading.Thread(target=send_scheduled_message, args=(chat_id, text, schedule_timestamp, stop_event))
  thread_id = f'{uuid.uuid4()}-telegram'
  scheduled_threads[thread_id] = thread
  thread_stop_events[thread_id] = stop_event
  thread.start()
  return thread_id

def cancel_scheduled_message(thread_id):
  print(f"Attempting to cancel message with thread ID: {thread_id}")
  if thread_id in thread_stop_events:
    thread_stop_events[thread_id].set()
    del thread_stop_events[thread_id]
    del scheduled_threads[thread_id]
    print(f"Message with thread ID: {thread_id} successfully cancelled.")
    return True
  print(f"Message with thread ID: {thread_id} not found.")
  return False

# Email
def send_scheduled_email(subject, message, from_email, recipient_list, schedule_timestamp, stop_event):
  delay = schedule_timestamp - time.time()
  if delay > 0 and not stop_event.wait(timeout=delay):
    send_mail(subject, message, from_email, recipient_list, html_message=message)
  else:
    print(f"Email to {recipient_list} cancelled or already executed.")

def schedule_email(subject, message, from_email, recipient_list, schedule_timestamp):
  stop_event = threading.Event()
  thread = threading.Thread(target=send_scheduled_email, args=(subject, message, from_email, recipient_list, schedule_timestamp, stop_event))
  thread_id = f'{uuid.uuid4()}-email'
  scheduled_threads[thread_id] = thread
  thread_stop_events[thread_id] = stop_event
  thread.start()
  return thread_id

def cancel_scheduled_email(thread_id):
  print(f"Attempting to cancel email with thread ID: {thread_id}")
  if thread_id in thread_stop_events:
    thread_stop_events[thread_id].set()
    del thread_stop_events[thread_id]
    del scheduled_threads[thread_id]
    print(f"Email with thread ID: {thread_id} successfully cancelled.")
    return True
  print(f"Email with thread ID: {thread_id} not found.")
  return False

# Discord
Authorization = settings.AUTHORIZATION

def send_scheduled_discord_message(channel_id, content, schedule_timestamp, stop_event):
  delay = schedule_timestamp - time.time()
  if delay > 0 and not stop_event.wait(timeout=delay):
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages'
    payload = {"content": content}
    headers = {"Authorization": Authorization}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
      print(f'Message sent successfully to channel {channel_id}')
    else:
      print(f'Failed to send message to channel {channel_id}')
  else:
    print(f"Discord message to {channel_id} cancelled or already executed.")

def schedule_discord_message(channel_id, content, schedule_timestamp):
  stop_event = threading.Event()
  thread = threading.Thread(target=send_scheduled_discord_message, args=(channel_id, content, schedule_timestamp, stop_event))
  thread_id = f'{uuid.uuid4()}-discord'
  scheduled_threads[thread_id] = thread
  thread_stop_events[thread_id] = stop_event
  thread.start()
  return thread_id

def cancel_scheduled_discord_message(thread_id):
  print(f"Attempting to cancel discord message with thread ID: {thread_id}")
  if thread_id in thread_stop_events:
    thread_stop_events[thread_id].set()
    del thread_stop_events[thread_id]
    del scheduled_threads[thread_id]
    print(f"Discord message with thread ID: {thread_id} successfully cancelled.")
    return True
  print(f"Discord message with thread ID: {thread_id} not found.")
  return False



