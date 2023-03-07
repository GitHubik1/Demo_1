from fastapi import FastAPI
from db.Database import engine, SessionLocal, create_all
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import datetime
from db import Models
import uvicorn
import re

# This code is written by Minuta18 (GitHubik1)
#
# Copyright (c) 2022 Samsonov Igor. All rights reserved

FIRST_RUN = True

SECRET_KEY = '9782a9ddebeb701f2df3e023873e735c45aa9b989a7fd6cd8867a42c740d1d28'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

phone_mask = re.compile('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
password_mask = re.compile('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

app = FastAPI()

def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get('/')
async def root():
    return {'Cringe': True}

@app.post('/auth/v.1.0/')
def auth(user: Models.UserCreateShema, db: SessionLocal = Depends(get_database)):
    db_user = db.query(Models.User).filter(Models.User.phone == user.phone).first()
    if db_user:
        if pwd_context.verify(user.password, db_user.hashed_password):
            return {'success': True, 'error': '', 'data': {'token': db_user.token, 'expires': db_user.expires_in}}
        else:
            return {'success': False, 'error': 'Неверен пароль', 'data': {}}
    else:
        if not phone_mask.match(user.phone):
            return {'success': False, 'error': 'Не валидный номер телефона', 'data': {}}
        if not password_mask.match(user.password):
            return {'success': False, 'error': 'Не достаточная сложность пароля', 'data': {}}
        password_hash = pwd_context.hash(user.password)
        access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.phone}, expires_delta=access_token_expires
        )
        new_user = Models.User(
            phone=user.phone, 
            hashed_password=password_hash, 
            token=access_token, 
            expires_in=(datetime.datetime.utcnow() + access_token_expires)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    return {'success': True, 'error': '', 'data': {'token': new_user.token, 'expires': new_user.expires_in}}

if __name__ == '__main__':
    if FIRST_RUN:
        create_all()
    uvicorn.run('Main:app', port=17200, reload=True)
