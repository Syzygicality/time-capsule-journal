from app.database import getenv

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from fastapi.exceptions import HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi import status

sg = SendGridAPIClient(api_key=getenv('SENDGRID_KEY'))

async def send_email(email, subject, html_content):
    message = Mail(
        from_email=('no-reply@edisonwang.dev', 'Time Capsule Journal'),
        to_emails=email,
        subject=subject,
        html_content=html_content)
    try:
        await run_in_threadpool(sg.send, message)
    except Exception as e:
        raise HTTPException(detail="Something went wrong. Please try again later.", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

async def send_verification_email(email, code):
    html_content = f"<p>Your verification code is: <strong>{code}</strong></p>"
    await send_email(email, "Time Capsule Journal 2FA Code", html_content)