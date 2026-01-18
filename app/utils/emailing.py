from app.database import getenv

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

async def send_email(email, subject, content):
    message = Mail(
        from_email=('no-reply@edisonwang.dev', 'Time Capsule Journal'),
        to_emails=email,
        subject=subject,
        html_content=content)
    try:
        sg = SendGridAPIClient(api_key=getenv('SENDGRID_KEY'))
        sg.send(message)
    except Exception as e:
        print(str(e))