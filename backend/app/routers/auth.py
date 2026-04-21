from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional

from .. import crud, models, schemas
from ..auth import verify_password, create_access_token, decode_access_token
from ..dependencies import get_db

router = APIRouter(prefix='/api/auth', tags=['auth'])


def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    if not authorization or not authorization.startswith('Bearer '):
        return None
    token = authorization.split(' ', 1)[1]
    credentials = decode_access_token(token)
    if not credentials or not credentials.sub:
        return None
    return crud.get_user_by_email(db, credentials.sub)

@router.post('/login', response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    access_token = create_access_token(subject=user.email, role=user.role)
    return {'access_token': access_token, 'token_type': 'bearer'}

@router.post('/register', response_model=schemas.UserRead)
def register(
    user_create: schemas.UserCreate,
    current_user: Optional[models.User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    existing = crud.get_user_by_email(db, user_create.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')

    if user_create.role == 'superadmin':
        admin_exists = db.query(models.User).filter(models.User.role == 'superadmin').first() is not None
        if admin_exists:
            if current_user is None or current_user.role != 'superadmin':
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')
    # Professors and students may register freely.
    user = crud.create_user(db, user_create)
    return user
