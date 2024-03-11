from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import argon2 as passlib_argon2
import os
import psycopg2
from psycopg2 import sql
from io import StringIO
import csv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

ETL_DB_NAME = os.getenv("ETL_DB_NAME")
ETL_DB_USER = os.getenv("ETL_DB_USER")
ETL_DB_PASSWORD = os.getenv("ETL_DB_PASSWORD")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


# Connect to the PostgreSQL user database
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

# Connect to the PostgreSQL etl database
conn_etl = psycopg2.connect(dbname=ETL_DB_NAME, user=ETL_DB_USER, password=ETL_DB_PASSWORD, host=DB_HOST, port=DB_PORT)


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


class StockItem(BaseModel):
    StockCode: str
    Description: str
    UnitPrice: float


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
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

def get_stock_from_db():
    with conn_etl.cursor() as cursor:
        cursor.execute("SELECT * FROM stock_table")
        return cursor.fetchall()


def add_stock_item_to_db(item: StockItem):
    with conn_etl.cursor() as cursor:
        cursor.execute(
            'INSERT INTO stock_table ("StockCode", "Description", "UnitPrice") VALUES (%s, %s, %s);',
            (item.StockCode, item.Description, item.UnitPrice)
        )
    conn_etl.commit()


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



@app.get("/stock/pulllist")
async def read_stock_table(current_user: User = Depends(get_current_active_user)):
    stock_table = get_stock_from_db()

    # Define headers
    headers = ["StockCode", "Description", "UnitPrice"]

    # Convert the data to CSV format
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    
    # Write headers
    csv_writer.writerow(headers)

    # Write data rows
    csv_writer.writerows(stock_table)

    # Create a StreamingResponse with CSV content
    response = StreamingResponse(iter([csv_data.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = 'attachment; filename="stock_table.csv"'
    return response

@app.post("/stock/additem", response_model=StockItem)
async def add_stock_item(item: StockItem, current_user: User = Depends(get_current_active_user)):
    add_stock_item_to_db(item)
    return item

#in real life front end would save token for certain time

#need to fake generate username and password because we don'T have a registration page
#pwd = get_password_hash("Anna123")
#print(pwd)
#and save hashed password in database
