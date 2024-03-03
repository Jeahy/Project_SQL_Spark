#dedicated layer for database interactions
#repository interface with abstract methods in the Repository Pattern

# dedicated layer for database interactions
# repository interface with abstract methods in the Repository Pattern
import sys
import os
sys.path.append(os.path.abspath('/home/pkn/ecompipeline/api'))

from abc import abstractmethod
from dto.user import User
from dto.activesession import ActiveSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends

class IUserRepository:
    @abstractmethod
    def register(self, user: User) -> User: pass

    @abstractmethod
    def create_access_token(self, data: dict, expires_delta): pass

    @abstractmethod
    def get_user_by_username(self, username: str): pass

    @abstractmethod
    def is_password_correct(self, form_data: OAuth2PasswordRequestForm = Depends()) -> bool: pass

    @abstractmethod
    def get_access_token(self, form_data: OAuth2PasswordRequestForm = Depends()): pass

    @abstractmethod
    def authenticate(self, token: str): pass

    @abstractmethod
    def register_token_in_session(self, token: str): pass

    @abstractmethod
    def logout(self, token: str): pass

    @abstractmethod
    def is_session_active(self, username: str): pass

    @abstractmethod
    def get_access_token_from_active_session(self, username: str): pass
