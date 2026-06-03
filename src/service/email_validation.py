from fastapi_mail import FastMail, MessageSchema, MessageType
from src.config import conf

async def send_reset_email(email: str, token: str):

#f"http://localhost:3000/reset-password?token={token}"
    reset_link = (
        f"https://www.linkedin.com/in/beatriz-andrade-94b38b233/"
    )

    message = MessageSchema(
        subject="Recuperação de Senha",
        recipients=[email],
        body=f"""
        Olá,

        Clique no link abaixo para redefinir sua senha:

        {reset_link}
        {token}

        Caso não tenha solicitado esta alteração,
        ignore este e-mail.
        """,
        subtype=MessageType.plain
    )

    fm = FastMail(conf)
    await fm.send_message(message)


async def send_validation_email(email: str):

    reset_link = (
        f"botar link aqui"
    )

    message = MessageSchema(
        subject="Recuperação de Senha",
        recipients=[email],
        body=f"""
        Olá,

        Clique no link abaixo para validar seu cadastro:

        {reset_link}

        """,
        subtype=MessageType.plain
    )

    fm = FastMail(conf)
    await fm.send_message(message)