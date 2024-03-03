#implementation of the IUserRepository Class
import sys
import os
sys.path.append(os.path.abspath('/home/pkn/ecompipeline/api'))

from repository.iuserrepository import IUserRepository
from dto.user import User
from dto.activesession import ActiveSession
from entity_manager.entity_manager import entity_manager
from sqlalchemy.orm import Session
from dotenv import load_dotenv


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends
from passlib.context import CryptContext
from datetime import timedelta, datetime
from passlib.hash import bcrypt
import jwt
from jwt import PyJWTError
from fastapi import HTTPException



dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

# CryptContext for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Use the get_session method from the instance
session = entity_manager.get_session()

class UserRepository(IUserRepository):
    def __init__(self):
        self.activeSessionsEntityManager = entity_manager.get_session()

    def register(self, user: User):
        db_user = self.get_user_by_username(user.username)

        if db_user is None:
            hashed_password = pwd_context.hash(user.password)
            db_user = User(username=user.username, password=hashed_password)

            # Add the user to the database
            with entity_manager.get_session() as session:
                session.add(db_user)
                session.commit()

            return user
        else:
            return False

    def create_access_token(self, data: dict, expires_delta):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, os.environ.get("SECRET_KEY"), algorithm=os.environ.get("ALGORITHM"))
        return encoded_jwt

    def get_user_by_username(self, username: str):
        with entity_manager.get_session() as session:
            return session.query(User).filter(User.username == username).first()

    def is_password_correct(self, form_data: OAuth2PasswordRequestForm = Depends()) -> bool:
        user = self.get_user_by_username(form_data.username)

        if user is None or not pwd_context.verify(form_data.password, user.password):
            return False

        return True

    def get_access_token(self, form_data: OAuth2PasswordRequestForm = Depends()):
        access_token_expires = timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")))
        access_token = self.create_access_token(
            data={"sub": form_data.username}, expires_delta=access_token_expires
        )
        return access_token

    def authenticate(self, token: str):
        try:
            payload = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM")])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=400, detail="Could not validate credentials, user not found.")

            # Check if the token has expired
            expiry_time = payload.get("exp")
            if expiry_time is None or expiry_time < datetime.utcnow().timestamp():
                self.activeSessionsEntityManager.query(ActiveSession).filter(ActiveSession.username == username).delete()
                self.activeSessionsEntityManager.commit()
                raise HTTPException(status_code=401, detail="Authentication failed, invalid or expired token.")

            # Check if the username exists in the active sessions
            session = self.activeSessionsEntityManager.query(ActiveSession).filter(ActiveSession.username == username).first()
            if not session:
                raise HTTPException(status_code=401, detail="User session not found.")

        except PyJWTError:
            raise HTTPException(status_code=401, detail="Authentication failed, invalid or expired token.")

    def register_token_in_session(self, token: str):
        try:
            payload = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM")])
            user, expiration_time = payload.get("sub"), payload.get("exp")
            expiration_datetime = datetime.utcfromtimestamp(expiration_time)

            new_active_session = ActiveSession(
                username=user,
                access_token=token,
                expiry_time=expiration_datetime
            )

            self.activeSessionsEntityManager.add(new_active_session)
            self.activeSessionsEntityManager.commit()
        except PyJWTError:
            raise HTTPException(status_code=401, detail="Authentication failed, invalid or expired token.")

    def logout(self, token: str):
        self.activeSessionsEntityManager.query(ActiveSession).filter(ActiveSession.access_token == token).delete()
        self.activeSessionsEntityManager.commit()

    def is_session_active(self, username: str):
        # First, check if the user has an active session
        existing_session = self.activeSessionsEntityManager.query(ActiveSession).filter(ActiveSession.username == username).first()
        if not existing_session:
            return False

        # If an active session exists, check if the token is still valid
        try:
            payload = jwt.decode(existing_session.access_token, os.environ.get("SECRET_KEY"),
                                 algorithms=[os.environ.get("ALGORITHM")])
            expiry_time = payload.get("exp")
            current_time = datetime.utcnow().timestamp()

            if expiry_time is None or expiry_time < current_time:
                # Token has expired
                self.activeSessionsEntityManager.delete_many({"username": username})
                return False
        
        except PyJWTError:
            # there was an error in processing the token, delete the session and return false as session is no longer active.
            self.activeSessionsEntityManager.delete_many({"username": username})
            return False

        return True

    def get_access_token_from_active_session(self, username: str):
        existing_session = self.activeSessionsEntityManager.find_one({"username": username})
        if existing_session is not None: return existing_session["access_token"]
        return None         
