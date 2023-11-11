from django.core.mail import send_mail
from django.conf import settings


def send_mail_to_user(ch, data):
    to = data['email']
    email_from = settings.EMAIL_HOST_USER
    audio_id = data['audio_id']
    subject = f" Your video file no.{audio_id} has been converted"
    message = f"""
        Dear {to},

        You recenlly ask to convert a video file to audio file. We want
        to inform you that your can your download file is ready

        click on the link below
        http://localhost:8000/api/v1/audio/{audio_id}/

        Best regard
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=email_from,
            recipient_list=[to],
            fail_silently=True
        )
        print("[*] Successfuly send email",)

    except Exception as err:
        print(err)
        return "Faild to send email to user"
