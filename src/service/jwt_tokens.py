from datetime import datetime, UTC, timedelta
from jose import jwt
from decouple import config

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

def create_access_token(data: dict):
    payload = data.copy()

    expire = datetime.now(UTC) + timedelta(minutes=1440)

    payload.update({
        "exp": expire,
        "type": "access"
    })

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    payload = data.copy()

    expire = datetime.now(UTC) + timedelta(days=7)

    payload.update({
        "exp": expire,
        "type": "refresh"
    })

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_reset_token(email: str):

    expire = datetime.now(UTC) + timedelta(minutes=15)

    payload = {
        "sub": email,
        "exp": expire,
        "type": "reset"
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )