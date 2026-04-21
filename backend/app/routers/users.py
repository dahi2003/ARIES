from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, get_db
from ..schemas import UserRead

router = APIRouter(prefix='/api/users', tags=['users'])

@router.get('/me', response_model=UserRead)
def read_current_user(current_user = Depends(get_current_user)):
    return current_user
