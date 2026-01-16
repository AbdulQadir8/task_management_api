#!/usr/bin/env python3
"""
Authentication Setup for FastAPI Builder Skill
Sets up authentication system with JWT tokens
"""

import argparse
import os
from typing import Dict, List

def generate_auth_setup() -> str:
    """Generate authentication setup code"""
    auth_code = '''from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os

from app.config import settings

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Token models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str
    id: int

def verify_password(plain_password: str, hashed_password: str):
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    """Hash a plain password"""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str, users_db: Dict[str, UserInDB]):
    """Authenticate a user by username and password"""
    user = users_db.get(username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "sub": str(data.get("sub", ""))})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current user from the JWT token in the request"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # In a real app, you would fetch the user from the database
    # This is just a placeholder implementation
    # user = get_user(username=token_data.username)
    # if user is None:
    #     raise credentials_exception
    # return user

    # Placeholder user - replace with database lookup
    from app.database import get_db
    from app.models.user import User as UserDB
    db = next(get_db())
    user = db.query(UserDB).filter(UserDB.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get the current active user (not disabled)"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
'''

    return auth_code

def generate_user_model() -> str:
    """Generate user model code"""
    model_code = '''from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(String, server_default=func.now())

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
'''

    return model_code

def generate_user_schemas() -> str:
    """Generate user schema code"""
    schema_code = '''from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
'''

    return schema_code

def generate_auth_routes() -> str:
    """Generate authentication routes"""
    route_code = '''from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    Token
)
from app.schemas.user import UserCreate, User
from app.models.user import User as UserDB
from app.config import settings

router = APIRouter(tags=["auth"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(UserDB).filter(
        (UserDB.username == user.username) | (UserDB.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = UserDB(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/users/me/", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
'''

    return route_code

def main():
    parser = argparse.ArgumentParser(description='Setup authentication for FastAPI')
    parser.add_argument('--output-dir', default='./app',
                       help='Output directory for auth files')

    args = parser.parse_args()

    # Create output directory structure
    os.makedirs(args.output_dir, exist_ok=True)

    auth_dir = os.path.join(args.output_dir, 'auth')
    models_dir = os.path.join(args.output_dir, 'models')
    schemas_dir = os.path.join(args.output_dir, 'schemas')
    routes_dir = os.path.join(args.output_dir, 'routes')

    os.makedirs(auth_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(schemas_dir, exist_ok=True)
    os.makedirs(routes_dir, exist_ok=True)

    # Generate content
    auth_content = generate_auth_setup()
    user_model_content = generate_user_model()
    user_schema_content = generate_user_schemas()
    auth_route_content = generate_auth_routes()

    # Write files
    with open(os.path.join(auth_dir, 'auth.py'), 'w') as f:
        f.write(auth_content)

    with open(os.path.join(models_dir, 'user.py'), 'w') as f:
        f.write(user_model_content)

    with open(os.path.join(schemas_dir, 'user.py'), 'w') as f:
        f.write(user_schema_content)

    with open(os.path.join(routes_dir, 'auth.py'), 'w') as f:
        f.write(auth_route_content)

    print("Authentication system setup completed!")
    print(f"Files created in {args.output_dir}/:")
    print("  auth/auth.py - Authentication utilities")
    print("  models/user.py - User database model")
    print("  schemas/user.py - User Pydantic schemas")
    print("  routes/auth.py - Authentication routes")

if __name__ == "__main__":
    main()