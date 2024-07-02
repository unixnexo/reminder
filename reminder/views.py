from django.http import HttpResponse
from django.core.mail import send_mail

def simple_email(request):

    send_mail(
        subject='hi mom',
        message='hi mom how u doing these days? this is me from sky',
        from_email='ali.unix.24@gmail.com',
        recipient_list=['unixnexo@gmail.com']
    )

    return HttpResponse('done')
