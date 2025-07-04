from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from jinja2 import Environment, FileSystemLoader
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Contacts App",
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates'
)

async def send_email(email: EmailStr, user_name: str, token: str, email_type: str):
    try:
        if email_type == "verify_email":
            subject = "Verify your email - Contacts App"
            template_name = "email_verify.html"
            link = f"{settings.base_url}/auth/verify_email/{token}"
        elif email_type == "reset_password":
            subject = "Reset your password - Contacts App"
            template_name = "email_reset_password.html"
            link = f"{settings.base_url}/auth/reset_password?token={token}"
        else:
            raise ValueError("Invalid email type specified.")

        message = MessageSchema(
            subject=subject,
            recipients=[email],
            template_body={"host": settings.base_url, "user_name": user_name, "link": link},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name=template_name)
        print(f"Email '{email_type}' sent successfully to {email}")

    except ConnectionErrors as e:
        print(f"Failed to send email to {email}: Connection error - {e}")

    except Exception as e:
        print(f"Failed to send email to {email}: An unexpected error occurred - {e}")

async def send_reset_password_email(email: str, token: str):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("reset_password.html")
    reset_link = f"{settings.frontend_base_url}/reset-password?token={token}"
    html = template.render(reset_link=reset_link)

    message = MessageSchema(
        subject= "Reset your password",
        recipients=[email],
        body=html,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)
