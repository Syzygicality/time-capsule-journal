from app.database import getenv
from app.models import Capsule, Conversation
from app.utils.encryption import decrypt_content

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from fastapi.exceptions import HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi import status
from pydantic import EmailStr
import html

sg = SendGridAPIClient(api_key=getenv('SENDGRID_KEY'))

async def send_email(email: EmailStr, subject: str, html_content: str) -> None:
    message = Mail(
        from_email=('no-reply@edisonwang.dev', 'Time Capsule Journal'),
        to_emails=email,
        subject=subject,
        html_content=html_content)
    try:
        await run_in_threadpool(sg.send, message)
    except Exception as e:
        raise HTTPException(detail="Something went wrong. Please try again later.", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

async def send_verification_email(email: EmailStr, code: int) -> None:
    html_content = f"<p>Your verification code is: <strong>{code}</strong></p>"
    await send_email(email, "Time Capsule Journal 2FA Code", html_content)

async def send_capsule_email(email: EmailStr, capsule: Capsule) -> None:
    html_content = f"""
    <p>One of your capsules has been released, buried since {capsule.creation_date.strftime("%Y-%m-%d %H:%M UTC")}. (ID: {capsule.id})</p><br>
    <p>{html.escape(decrypt_content(capsule.content)).replace('\n', '<br>')}</p><br>
    <p>For more information, visit <a href="https://journal.edisonwang.dev">the docs.</a></p>
    """
    await send_email(email, "A message from your past self...", html_content)

async def send_conversation_email(email: EmailStr, conversation: Conversation):
    capsule = conversation.latest_capsule
    html_content = f"""
    <p>One of your capsules has been released, buried since {capsule.creation_date.strftime("%Y-%m-%d %H:%M UTC")}. (ID: {capsule.id})</p><br>
    <p>{html.escape(decrypt_content(capsule.content)).replace('\n', '<br>')}</p><br>
    <p>This capsule is part of a conversation:</p><br>
    """
    capsule = capsule.replying_to
    while capsule:
        html_content += f"""
        <p>Sent at {capsule.creation_date.strftime("%Y-%m-%d %H:%M UTC")}, (ID: {capsule.id})</p><br>
        <p>{html.escape(decrypt_content(capsule.content)).replace('\n', '<br>')}</p><br>
        """
        capsule = capsule.replying_to
    html_content += """<p>For more information, visit <a href="https://journal.edisonwang.dev">the docs.</a></p>"""
    await send_email(email, "A message from your past self...", html_content)
    
