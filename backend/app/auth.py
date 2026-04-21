from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

from .config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from .schemas import TokenPayload

pwd_context = CryptContext(schemes=['pbkdf2_sha256', 'bcrypt'], deprecated='auto')
ALGORITHM = 'HS256'


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {'exp': expire, 'sub': subject, 'role': role}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(sub=payload.get('sub'), role=payload.get('role'))
    except JWTError:
        return None
