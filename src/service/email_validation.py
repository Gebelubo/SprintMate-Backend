from fastapi_mail import FastMail, MessageSchema, MessageType
from src.config import conf, FRONTEND_URL

async def send_reset_email(email: str, token: str):

    reset_link = f"{FRONTEND_URL}/auth/reset-password?token={token}"
    print("Entrou em send_reset_email")

    message = MessageSchema(
        subject="Recuperação de Senha",
        recipients=[email],
        body=f"""
        Olá,

        Clique no link abaixo para redefinir sua senha:

        {reset_link}

        Caso não tenha solicitado esta alteração,
        ignore este e-mail.
        """,
        subtype=MessageType.plain
    )

    fm = FastMail(conf)
    print("SAIUUUU")
    await fm.send_message(message)


async def send_validation_email(email: str):

    reset_link = f"{FRONTEND_URL}/auth/check-email?email={email}"

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