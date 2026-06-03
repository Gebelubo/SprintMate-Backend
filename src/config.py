import os

from fastapi_mail import ConnectionConfig
from dotenv import load_dotenv

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = '9f4c2b7a8d3e1f6c0a5b9d8e7f1a2c4b6d9e0f3a7b1c5d8e2f6a9c0b4d7e1f5'
ALGORITHM = 'HS256'

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_USERNAME"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)