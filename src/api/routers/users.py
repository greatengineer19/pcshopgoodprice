from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy import (select, func, delete, text, and_, or_)
from src.schemas import (UserAPIResponse, UserParams, UserRoleParams)
from src.models import (CartLine, User, ComputerComponent, PaymentMethod)
import logging
from src.api.s3_dependencies import ( bucket_name, s3_client )
from sqlalchemy.orm import joinedload, Session
from src.api.dependencies import get_db
from datetime import datetime, timedelta
from utils.auth import ( oauth2_scheme, decode_jwt_and_pass_expiry_errors, create_access_token, create_refresh_token )

router = APIRouter(
    prefix='/api/user'
)

@router.get("", response_model=UserAPIResponse)
def show_user(
        token: str = Depends(oauth2_scheme),
        role: UserRoleParams = Query(None),
        db: Session = Depends(get_db)
    ):
    try:
        user = None
        valid_token = False
        if not role:
            user = decode_jwt_and_pass_expiry_errors(token, db)
            valid_token = True if user else valid_token
        if not user:
            role = 1 if role == "buyer" else 0
            user_name = 'super_buyer' if role == 1 else "admin_seller"
        
            user = (
                db.query(User)
                .filter(and_(User.role == role, User.username == user_name))
                .first()
            )
            

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if (user.refresh_token is None or user.refresh_token_expiry_at < datetime.utcnow()):
            expires_at = datetime.utcnow() + timedelta(minutes=3600)
            new_refresh_token = create_refresh_token(user.id, expires_at)
            user.refresh_token_expiry_at = expires_at
            user.refresh_token = new_refresh_token
            db.add(user)
            db.commit()

        access_token = token if valid_token else create_access_token(user.id, 30)
        response = {
            'user': {
                'id': user.id,
                'fullname': user.fullname,
                'role': user.role
            },
            'access_token': access_token,
            'refresh_token': user.refresh_token
        }

        return response
    except Exception as e:
        logging.error(f"An error occurred in index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/show-default", response_model=UserAPIResponse)
def show_default_user(db: Session = Depends(get_db)):
    try:
        user = (
            db.query(User)
            .filter(and_(User.role == 0, User.username == 'admin_seller'))
            .first()
        )      

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if (user.refresh_token is None or user.refresh_token_expiry_at < datetime.utcnow()):
            expires_at = datetime.utcnow() + timedelta(minutes=3600)
            new_refresh_token = create_refresh_token(user.id, expires_at)
            user.refresh_token_expiry_at = expires_at
            user.refresh_token = new_refresh_token
            db.add(user)
            db.commit()

        access_token = create_access_token(user.id, 30)
        response = {
            'user': {
                'id': user.id,
                'fullname': user.fullname,
                'role': user.role
            },
            'access_token': access_token,
            'refresh_token': user.refresh_token
        }

        return response
    except Exception as e:
        if e.status_code:
            raise e

        logging.error(f"An error occurred in index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
