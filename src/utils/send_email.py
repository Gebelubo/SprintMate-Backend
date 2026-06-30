from fastapi_mail import FastMail, MessageSchema, MessageType
from src.config import conf, FRONTEND_URL


async def send_project_invite_email(
    email: str,
    project_id: int,
    project_name: str,
    subject: str,
):
    invite_link = (
        f"{FRONTEND_URL}/invite/{project_id}"
    )

    body = f"""
    Você foi convidado para participar do projeto:

    {project_name}

    Clique no link abaixo para aceitar o convite:

    {invite_link}
    """

    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype=MessageType.plain
    )

    fm = FastMail(conf)
    await fm.send_message(message)