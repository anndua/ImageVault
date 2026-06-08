from passlib.context import CryptContext
from jose import jwt  # type: ignore[import]
from datetime import datetime, timedelta
from jose import JWTError
from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from model import User
from config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )






def create_access_token(data:dict):
    to_encode=data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update(
        {"exp": expire}
    )

    # Ensure algorithm and secret key are valid strings for jose.jwt
    alg = ALGORITHM or "HS256"
    secret = SECRET_KEY or ""

    encoded_jwt = jwt.encode(
        to_encode,
        secret,
        algorithm=alg
    )

    return encoded_jwt

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    alg = ALGORITHM or "HS256"
    secret = SECRET_KEY or ""

    payload=jwt.decode(
        token,
        secret,
        algorithms=[alg]
    )
    user_id=payload.get("sub")
    if not user_id:
         raise HTTPException(
        status_code=401,
        detail="Invalid token"
    )
    statement = select(User).where(
        User.id == int(user_id)
    )

    user = session.exec(statement).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


    

        


