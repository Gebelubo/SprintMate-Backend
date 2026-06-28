from fastapi_mail import FastMail, MessageSchema, MessageType
from src.config import conf, FRONTEND_URL

async def send_project_invite_email(
    email: str,
    project_id: int,
    body: str,
    subject: str
):

    invite_link = (
        f"{FRONTEND_URL}/invite/{project_id}"
    )

    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype=MessageType.plain
    )

    fm = FastMail(conf)
    await fm.send_message(message)