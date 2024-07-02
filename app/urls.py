from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/', views.SendSignInEmail.as_view(), name='auth'),
    path('sign-out/', views.sign_out, name='sign_out'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('user/settings/', views.user_settings, name='settings'),
    path('user/add-reminder/', views.add_reminder, name='add_reminder'),
    path('user/delete-reminder/<int:reminder_id>/', views.delete_reminder, name='delete_reminder'),
    path('user/reminder/refresh/', views.refresh_reminders, name='reminder_refresh'),
    path('user/settings/send_to_email/', views.toggle_send_to_email, name='toggle_send_to_email'),
    path('user/settings/send_to_telegram/', views.toggle_send_to_telegram, name='toggle_send_to_telegram'),
    path('user/settings/send_to_discord/', views.toggle_send_to_discord, name='toggle_send_to_discord'),
]
