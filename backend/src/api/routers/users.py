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
from utils.auth import ( get_current_user, create_access_token, create_refresh_token )

router = APIRouter(
    prefix='/api/user'
)

@router.get("", response_model=UserAPIResponse)
def user_by_role(
        role: UserRoleParams = Query(None),
        db: Session = Depends(get_db)
    ):
    try:
        role = 0 if role == "seller" else 1
    
        user = (
            db.query(User)
              .filter(User.role == role)
              .first()
        )

        if user is None:
            return { 'user': {}, 'access_token': '', 'refresh_token': '' }
        
        if user.refresh_token is not None:
            if user.refresh_token_expiry_at < datetime.utcnow():
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
        logging.error(f"An error occurred in index: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
