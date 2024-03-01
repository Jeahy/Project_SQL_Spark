from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import psycopg2
from psycopg2 import sql


DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

#to create secret key run: openssl rand -hex 32

# Connect to the PostgreSQL database
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)


class Token(BaseModel): #used for validation of json data 
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None


class User(BaseModel):
    username: str
    email: str or None = None
    full_name: str or None = None
    disabled: bool or None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI() #create instance of fastapi, referred to in uvicorn command

#hashed passwords avoid saving password itself somewhere

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# Function to get user from PostgreSQL database
def get_user_from_db(username: str):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        user_data = cursor.fetchone()
    if user_data:
        return UserInDB(**dict(zip(["username", "email", "full_name", "hashed_password", "disabled"], user_data)))
    return None

def authenticate_user(username: str, password: str):
    user = get_user_from_db(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy() #copy data above so it doesn't affect original
    if expires_delta: #if we passed a delta then it expires then:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire}) #encoding whatever is passed as "data" plus expiry data
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):#calls oath function which parses token out and gives access to it
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) #parse out token
        username: str = payload.get("sub") #get user that was encoded in token
        if username is None:  #make user user exits
            raise credential_exception

        token_data = TokenData(username=username) #if user exists we get data associated with it
    except JWTError:
        raise credential_exception

    user = get_user_from_db(username=token_data.username) #make sure user is part of database
    if user is None:
        raise credential_exception

    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled: #if user disabled do this (relying on get_current_user function):
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user #if not do return current user

    #function to able/enable users from logging in


@app.post("/token", response_model=Token) #this is route taken when signing in that gives us our token
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"} #this is the json data token


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)): #depends on active user
    return current_user


@app.get("/users/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": 1, "owner": current_user}]


#in real life front end would save token for certain time

#need to fake generate username and password because we don'T have a registration page
#pwd = get_password_hash("Anna123")
#print(pwd)
#and save hashed password in database
