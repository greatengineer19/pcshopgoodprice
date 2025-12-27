from sqlalchemy.orm import Session
from utils.password import secure_pwd
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jose import jwt, JWTError
from config import setting
from datetime import date, datetime, timedelta, time, timezone
from fastapi import HTTPException, status, Request
from typing import Union, Any, Optional
import jwt
from jwt import InvalidTokenError
from fastapi import Depends
from src.api.session_db import get_db
from src.models import ( User )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def decode_jwt_and_pass_expiry_errors(token: str, db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decodeJWT(token)
    if payload is None:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decodeJWT(token)
        if payload is None:
            raise credentials_exception
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise credentials_exception

        return user
    except jwt.ExpiredSignatureError:
        return False
    except jwt.PyJWTError:
        return False
    finally:
        db.close()

def create_access_token(subject: Union[str, Any], expires_delta: Optional[int] = None) -> str:
    additional_time = expires_delta if expires_delta is not None else setting.ACCESS_TOKEN_EXPIRE_MINUTES
    expires_delta = datetime.now(timezone.utc) + timedelta(minutes=additional_time)

    to_encode = { "exp": expires_delta, "sub": str(subject) }
    encoded_jwt = jwt.encode(to_encode, setting.JWT_SECRET_KEY, setting.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any], expires_at: int) -> str:
    to_encode = { "exp": expires_at, "sub": str(subject) }
    encoded_jwt = jwt.encode(to_encode, setting.JWT_REFRESH_KEY, setting.JWT_ALGORITHM)
    return encoded_jwt

def decodeJWT(jwtoken: str):
    try:
        payload = jwt.decode(jwtoken, setting.JWT_SECRET_KEY, setting.JWT_ALGORITHM)
        return payload
    except InvalidTokenError:
        return None
    
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            token = credentials.credentials
            if not self.verify_jwt(token):
                raise HTTPException(status_code=403, detail="Invalid token or expired token")
            return token
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code")
        
    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = decodeJWT(jwtoken)
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.JWTError:
            return False

