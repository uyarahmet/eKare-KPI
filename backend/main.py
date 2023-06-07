import os

import pandas as pd
from fastapi.openapi.models import Response
from fastapi.params import File
from fastapi.responses import HTMLResponse
import sqlite3
import numpy as np
from matplotlib import pyplot as plt
import pandas
import csv
import prompt
import calendar

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Annotated, Union, Optional

from fastapi import Depends, FastAPI, HTTPException, status, Form, Request, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, validator

from fastapi.templating import Jinja2Templates
import json

from starlette.responses import FileResponse

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "143169a6c0fe9c5c55cb347539682a52f3afecf6e1e780135bc475f3c8c9bcd0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "taylan": {
        "username": "taylan",
        "full_name": "taylan akyurek",
        "email": "aakyurek17@gmail.comm",
        "hashed_password": "$2b$12$qUcml2YPMHxNsZ.ANcTq5uWVjkqQ/oYpwroXC3hTCWzizoKYY.146",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: Union[str, None] = None
    password: Union[str, None] = None
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

templates = Jinja2Templates(directory="templates")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(conn, username: str, password: str):
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE username='{username}';")
    user = cur.fetchone()
    return user


def authenticate_user(username: str, password: str):
    conn = create_connection()
    create_user_table(conn)
    user = get_user(conn, username, password)
    if not user:
        print(f"User {username} does not exist")

        return False

    if not verify_password(password, user[2]):
        print(f"Wrong password")
        return False

    print(f"User {username} authenticated successfully")
    userObj = User()
    userObj.username = user[1]
    userObj.password = user[2]

    return userObj


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...)):
    conn = create_connection()
    create_user_table(conn)
    # Check if the username already exists
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE username='{username}';")
    user = cur.fetchone()

    if user:

        return {"fail message": "user already exists"}
    else:
        insert_user(conn, username, get_password_hash(password))
        return {"success message": get_password_hash(password)}


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    conn = create_connection()
    create_user_table(conn)
    userFroDb = get_user(conn, username=token_data.username)
    user = User()
    user.username = userFroDb[1]
    user.password = userFroDb[2]

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Connect to the SQLite database
conn = sqlite3.connect("databases/ekare.db")
cursor = conn.cursor()

# Create the necessary table if it doesn't exist
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS patient_data (
        group_name TEXT,
        account_name TEXT,
        site_name TEXT,
        id_patient INTEGER,
        gender TEXT,
        is_enabled INTEGER,
        Age INTEGER,
        id_wound INTEGER,
        onset TEXT,
        type TEXT,
        secondary_type TEXT,
        primary_location TEXT,
        secondary_location TEXT,
        is_active INTEGER,
        status TEXT,
        is_deleted INTEGER,
        id_measurement INTEGER,
        Wound_id_wound INTEGER,
        uid TEXT,
        avg_depth REAL,
        maximum_depth REAL,
        maximum_width REAL,
        maximum_length REAL,
        perimeter REAL,
        area REAL,
        volume REAL,
        date TEXT,
        granulation REAL,
        slough REAL,
        eschar REAL,
        taken_with_sensor INTEGER,
        quality_index REAL,
        source TEXT,
        device TEXT,
        path TEXT
    )
    """
)

"""
# Read the CSV file and insert data into the database
with open("inSightDataCR_May2020_Koc.csv", newline="") as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # Skip the header row

    # Insert each row of data into the database
    for row in csv_reader:
        cursor.execute(
            '''
            INSERT INTO patient_data
            (group_name, account_name, site_name, id_patient, gender, is_enabled, Age, id_wound, onset, type, secondary_type,
            primary_location, secondary_location, is_active, status, is_deleted, id_measurement, Wound_id_wound, uid, avg_depth,
            maximum_depth, maximum_width, maximum_length, perimeter, area, volume, date, granulation, slough, eschar,
            taken_with_sensor, quality_index, source, device, path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            row,
        )
"""
# Commit the changes and close the connection
conn.commit()
conn.close()


# Define a function to create database connection
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('databases/users.db')
        print("Connected to SQLite database")
    except sqlite3.Error as e:
        print(e)
    return conn


# Define a function to create a user table
def create_user_table(conn):
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL);''')
        print("User table created successfully")
    except sqlite3.Error as e:
        print(e)


# Define a function to create database connection
def create_data_connection():
    conn = None
    try:
        conn = sqlite3.connect('data.db')
        print("Connected to SQLite database")
    except sqlite3.Error as e:
        print(e)
    return conn


# Define a function to create a wound data table
def create_data_table(conn):
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS data
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                patient_name TEXT NOT NULL)
                doctor TEXT NOT NULL);''')
        print("woundcare data table created successfully")
        insert_patient(conn, "1234", "taylan", "asli")
    except sqlite3.Error as e:
        print(e)


# Define a function to insert a user into the table
def insert_user(conn, username, password):
    try:
        conn.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}');")
        conn.commit()
        print(f"User {username} inserted successfully")
    except sqlite3.Error as e:
        print(e)


def insert_patient(conn, patient_id, patient_name, doctor):
    try:
        conn.execute(
            f"INSERT INTO data (patient_id, patient_name, doctor) VALUES ('{patient_id}', '{patient_name}', '{doctor}');")
        conn.commit()
        print(f"Patient {patient_id} inserted successfully")
    except sqlite3.Error as e:
        print(e)


# Define a function to authenticate user


# Define a route for the login page (test endpoint for authorization functions)
@app.get("/", response_class=HTMLResponse)
def main_page():
    return """
    <html>
<html>
        <head>
            <title>Login Page</title>
            <link rel="stylesheet" href="/static/style.css">
            <style>
                /* Styling for the container div */
                .container {
                    background-color: #f2f2f2;
                    border-radius: 5px;
                    padding: 20px;
                    margin: 50px auto;
                    width: 400px;
                }

                /* Styling for the h1 tags */
                h1 {
                    font-size: 28px;
                    text-align: center;
                }

                /* Styling for the hr tag */
                hr {
                    border: 0;
                    border-top: 1px solid #ccc;
                    margin: 20px 0;
                }

                /* Styling for the label tags */
                label {
                    font-size: 18px;
                    display: block;
                    margin-bottom: 10px;
                }

                /* Styling for the input tags */
                input[type=text], input[type=password] {
                    width: 100%;
                    padding: 12px 20px;
                    margin: 8px 0;
                    box-sizing: border-box;
                    border: 2px solid #ccc;
                    border-radius: 4px;
                }

                /* Styling for the submit buttons */
                button[type=submit] {
                    background-color: #4CAF50;
                    color: white;
                    padding: 14px 20px;
                    margin: 10px 0;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    width: 100%;
                }

                /* Styling for the link button */
                button[type=button] {
                    background-color: #4CAF50;
                    color: white;
                    padding: 14px 20px;
                    margin: 10px 0;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    width: 100%;
                }

                /* Styling for the login button */
                .loginbtn {
                    background-color: #4CAF50;
                }

                /* Styling for the signup button */
                .signupbtn {
                    background-color: #f44336;
                }

                /* Styling for the cancel button */
                .cancelbtn {
                    background-color: #ccc;
                }

                /* Styling for the error message */
                .error {
                    color: red;
                    font-size: 16px;
                    margin-top: 10px;
                }
            </style>
        </head>
        <body>
            <form method="post" action="/token">
                <div class="container">
                    <h1>Login</h1>
                    <hr>
                    <label for="username"><b>Username</b></label>
                    <input type="text" placeholder="Enter Username" name="username" required>
                    <label for="password"><b>Password</b></label>
                    <input type="password" placeholder="Enter Password" name="password" required>
                    <hr>
                    <button type="submit" class="loginbtn">Login</button>
                </div>
            </form>

            <form method="post" action="/signup">
                <div class="container">
                    <h1>Sign Up</h1>
                    <hr>
                    <label for="username"><b>Username</b></label>
                    <input type="text" placeholder="Enter Username" name="username" required>
                    <label for="password"><b>Password</b></label>
                    <input type="password" placeholder="Enter Password" name="password" required>
                    <hr>
                    <button type="submit" class="signupbtn">Sign Up</button>
                </div>
            </form>
            <form method="get" action="/update_dataset_page">
                <div class="container">
                    <h2>Update Dataset</h2>
                    <form method="post" action="/update_dataset_page">
                        <input type="submit" value="Go to Update Dataset Page" class="updatebtn">
                    </form>
                </div>
            </form>
        </body>
    </html>
    """


DATABASE_URL = "pie_chart.db"


def create_segments_table(conn):
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS segments
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                value INTEGER NOT NULL);''')
        print("Segments table created successfully")
    except sqlite3.Error as e:
        print(e)


# create toy database
def create_sample_data(conn):
    sample_data = [
        {"label": "Red", "value": 100},
        {"label": "Blue", "value": 100},
        {"label": "Yellow", "value": 100}
    ]

    cur = conn.cursor()
    for data in sample_data:
        cur.execute("SELECT COUNT(*) FROM segments WHERE label=?", (data["label"],))
        count = cur.fetchone()[0]

        if count == 0:
            cur.execute("INSERT INTO segments (label, value) VALUES (?, ?)", (data["label"], data["value"]))
        else:
            cur.execute("UPDATE segments SET value=? WHERE label=?", (data["value"], data["label"]))

    conn.commit()


def get_segments(conn):
    cur = conn.cursor()
    cur.execute("SELECT label, value FROM segments")
    return cur.fetchall()


conn = sqlite3.connect(DATABASE_URL)
create_segments_table(conn)
create_sample_data(conn)


@app.get("/visualize", response_class=HTMLResponse)
async def pie_chart(request: Request):
    segments = get_segments(conn)
    labels = [segment[0] for segment in segments]
    values = [segment[1] for segment in segments]
    print(labels)
    print(values)

    chart_data = {
        "labels": labels,
        "values": values,
        "background_colors": ["rgba(255, 99, 132, 0.2)", "rgba(54, 162, 235, 0.2)", "rgba(255, 206, 86, 0.2)"],
        "border_colors": ["rgba(255, 99, 132, 1)", "rgba(54, 162, 235, 1)", "rgba(255, 206, 86, 1)"]
    }

    return templates.TemplateResponse("chart.html", {"request": request, "chart_data": json.dumps(chart_data)})


class PatientData(BaseModel):
    group_name: str
    account_name: str
    site_name: str
    id_patient: int
    gender: str
    is_enabled: bool
    Age: int
    id_wound: int
    onset: str
    type: str
    secondary_type: str
    primary_location: str
    secondary_location: str
    is_active: bool
    status: str
    is_deleted: bool
    id_measurement: int
    Wound_id_wound: int
    uid: str
    avg_depth: float
    maximum_depth: float
    maximum_width: float
    maximum_length: float
    perimeter: float
    area: float
    volume: float
    date: str
    granulation: float
    slough: float
    eschar: float
    taken_with_sensor: bool
    quality_index: float
    source: str
    device: str
    path: str


@app.get("/update_dataset_page", response_class=HTMLResponse)
async def update_dataset_page(request: Request):
    return templates.TemplateResponse("update_dataset.html", {"request": request})


def custom_date_parser(date_str: Optional[str]) -> Optional[datetime.date]:
    if date_str is not None and not date_str.startswith("group_name"):
        date_str = date_str.strip()
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
    return None


"""
# Methods used to preprocess the inital db imported and the basis db structure is formed which will be maintained by the
# data updating methods.
def custom_date_parser(x):
    try:
        return pd.to_datetime(pd.to_datetime(x, format='%m/%d/%y %H:%M').strftime('%Y-%m-%d %H:%M'))
    except ValueError:
        return pd.to_datetime(pd.to_datetime(x, format='%m/%d/%y').strftime('%Y-%m-%d'))

# Load data
df = pd.read_csv('inSightDataCR_May2020_Koc.csv', parse_dates=['onset', 'date'], date_parser=custom_date_parser)

# Convert booleans
bool_cols = ['is_enabled', 'is_active', 'is_deleted', 'taken_with_sensor']
df[bool_cols] = df[bool_cols].astype('boolean')

# Convert integers
int_cols = ['id_patient', 'Age', 'id_wound', 'primary_location', 'secondary_location', 'id_measurement',
            'Wound_id_wound']
df[int_cols] = df[int_cols].astype('Int64')

# Convert floats
float_cols = ['avg_depth', 'maximum_depth', 'maximum_width', 'maximum_length', 'perimeter', 'area', 'volume',
              'quality_index', 'granulation', 'slough', 'eschar']
df[float_cols] = df[float_cols].astype('float')

# Convert strings
str_cols = ['group_name', 'account_name', 'site_name', 'gender', 'type', 'secondary_type', 'status', 'uid',
            'source', 'device', 'path']
df[str_cols] = df[str_cols].astype('str')
"""
df = pd.read_csv('inSightDataCR_May2020_Koc.csv', parse_dates=['onset', 'date'])


@app.post("/update_dataset")
async def update_dataset(file: UploadFile = File(...)):
    # Save the uploaded CSV file to disk
    with open("temp/sample.csv", "wb") as f:
        f.write(file.file.read())

    # Load the uploaded CSV file into a DataFrame
    df_new = pd.read_csv("temp/sample.csv", parse_dates=["onset", "date"], date_parser=custom_date_parser)

    # Create a connection to the database
    conn = sqlite3.connect("databases/ekare.db")
    cursor = conn.cursor()

    # Insert the new data into the patient_data table
    df_new.to_sql("patient_data", conn, if_exists="append", index=False)

    # Close the database connection
    cursor.close()
    conn.close()

    return {"message": "Dataset updated successfully."}


@app.post("/add_entry")
async def add_entry(entry: PatientData):
    """
    Adds a new patient entry to the data.

    Args:
        entry: The patient data to add.

    Returns:
        A dictionary with a detail of the operation status.
    """
    # Create a database connection
    conn = sqlite3.connect("databases/ekare.db")
    cursor = conn.cursor()

    # Convert the patient data to a dictionary
    entry_dict = entry.dict()

    # Check if the patient ID is a positive number
    if entry_dict['id_patient'] <= 0:
        raise HTTPException(status_code=422, detail="Invalid id_patient. Please enter a value greater than 0.")

    # Check if the age is a valid number between 0 and 120
    if entry_dict['Age'] < 0 or entry_dict['Age'] > 120:
        raise HTTPException(status_code=422, detail="Invalid age. Please enter a value between 0 and 120.")

    # Check if the gender is either 'M' or 'F'
    if entry_dict['gender'] not in ['M', 'F']:
        raise HTTPException(status_code=422, detail="Invalid gender. Please enter 'M' or 'F'.")

    # Check if the status is either 'active', 'healed', or 'closed'
    if entry_dict['status'] not in ['active', 'healed', 'closed']:
        raise HTTPException(status_code=422, detail="Invalid status. Please enter 'active', 'healed', or 'closed'.")

    # Check if the is_deleted, is_active, and is_enabled fields are boolean values
    if not isinstance(entry_dict['is_deleted'], bool):
        raise HTTPException(status_code=422, detail="Invalid is_deleted. Please enter a boolean value (True/False).")

    if not isinstance(entry_dict['is_active'], bool):
        raise HTTPException(status_code=422, detail="Invalid is_active. Please enter a boolean value (True/False).")


from fastapi import Query


@app.get("/query")
async def execute_query(query: str = Query(...)):
    conn = sqlite3.connect("databases/ekare.db")
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"query_result": result}


@app.get("/total_patients")  # Returns total unique patients in the dataset
async def get_total_patients():
    conn = sqlite3.connect("databases/ekare.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT id_patient) FROM patient_data")
    total_patients = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {"total_patients": total_patients}


@app.get("/patients_by_gender")  # Returns count of patients grouped by gender
async def get_patients_by_gender():
    conn = sqlite3.connect("databases/ekare.db")
    cursor = conn.cursor()
    cursor.execute("SELECT gender, COUNT(DISTINCT id_patient) FROM patient_data GROUP BY gender")
    patients_by_gender = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return {"patients_by_gender": patients_by_gender}


@app.get("/active_patients_by_gender")  # Returns count of active patients grouped by gender
async def get_active_patients_by_gender():
    df['gender'] = df['gender'].fillna('Unknown')
    df['is_enabled'] = df['is_enabled'].fillna(False).astype(bool)
    active_patients_by_gender = df[df['is_enabled']: True].groupby('gender')['id_patient'].nunique().to_dict()
    return {"Active patients categorised by Gender": active_patients_by_gender}


@app.get("/patients_by_age_group")  # Returns count of patients grouped by age groups
async def get_patients_by_age_group():
    df['Age'] = df['Age'].fillna(df['Age'].mean())
    bins = [0, 18, 30, 40, 50, 60, 70, 120]
    labels = ['<18', '18-29', '30-39', '40-49', '50-59', '60-69', '70>']
    df['age_group'] = pd.cut(df['Age'], bins=bins, labels=labels)
    patients_by_age_group = df.groupby('age_group')['id_patient'].nunique().to_dict()
    return {"Patients categorised by Age": patients_by_age_group}


@app.get("/new_patients_by_year/{year}")
async def get_new_patients_by_year(year: int):
    filename = "inSightDataCR_May2020_Koc.csv"

    new_patients_by_year = {}

    with open(filename, "r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            onset = row["onset"]
            if onset.startswith(str(year)):
                month = int(onset[5:7])
                month_name = calendar.month_name[month]
                if month_name not in new_patients_by_year:
                    new_patients_by_year[month_name] = 0
                new_patients_by_year[month_name] += 1

    return {"new_patients_by_year": new_patients_by_year}


@app.get("/patients_by_site")  # Returns count of patients grouped by site name
async def get_patients_by_site():
    patients_by_site = df.groupby('site_name')['id_patient'].nunique().to_dict()
    return {"patients_by_site": patients_by_site}


@app.get("/common_wound_types")  # Returns common wound types in the dataset
async def get_common_wound_types():
    df_nonull = df.dropna(subset=['type'])
    common_wound_types = df_nonull.groupby('id_wound')['type'].first().value_counts().to_dict()
    return {"common_wound_types": common_wound_types}


@app.get("/common_secondary_types")  # Returns common secondary wound types in the dataset
async def get_common_secondary_types():
    df_nonull = df.dropna(subset=['secondary_type'])
    common_secondary_types = df_nonull.groupby('id_wound')['secondary_type'].first().value_counts().to_dict()
    return {"common_secondary_types": common_secondary_types}


@app.get("/common_primary_locations")  # Returns common primary wound locations in the dataset
async def get_common_primary_locations():
    df_nonull = df.dropna(subset=['primary_location'])
    common_primary_locations = df_nonull.groupby('id_wound')['primary_location'].first().value_counts().to_dict()
    return {"common_primary_locations": common_primary_locations}


@app.get("/common_secondary_locations")  # Returns common secondary wound locations in the dataset
async def get_common_secondary_locations():
    df_nonull = df.dropna(subset=['secondary_location'])
    common_secondary_locations = df_nonull.groupby('id_wound')['secondary_location'].first().value_counts().to_dict()
    return {"common_secondary_locations": common_secondary_locations}


# WOUND STATUS
@app.get("/total_wounds")  # Returns total unique wounds in the dataset
async def get_total_wounds():
    total_wounds = df['id_wound'].nunique()
    return {"total_wounds": total_wounds}


@app.get("/new_wounds_by_year/{year}")
async def get_new_wounds_by_year(year: int):
    filename = "inSightDataCR_May2020_Koc.csv"

    df = pd.read_csv(filename)

    df['onset'] = pd.to_datetime(df['onset'])

    start_date = pd.to_datetime(f"{year}-01-01")
    end_date = start_date + pd.DateOffset(years=1)

    new_wounds = df[(df['onset'] >= start_date) & (df['onset'] < end_date)]
    new_wounds_by_month = new_wounds.groupby(new_wounds['onset'].dt.month)['id_wound'].nunique()

    month_names = [calendar.month_name[i] for i in new_wounds_by_month.index]

    new_wounds_by_month_dict = dict(zip(month_names, new_wounds_by_month))

    total_new_wounds = new_wounds['id_wound'].nunique()

    return {"new_wounds_by_year": new_wounds_by_month_dict, "total_new_wounds": total_new_wounds}


@app.get("/total_measurements")  # Returns the total unique measurements in the dataset
async def get_total_measurements():
    total_measurements = df['id_measurement'].nunique()
    return {"total_measurements": total_measurements}


@app.get("/new_measurements_by_year/{year}")
async def get_new_measurements_by_year(year: int):
    filename = "inSightDataCR_May2020_Koc.csv"

    df = pd.read_csv(filename)

    df['date'] = pd.to_datetime(df['date'])

    start_date = pd.to_datetime(f"{year}-01-01")
    end_date = start_date + pd.DateOffset(years=1)

    new_measurements = df[(df['date'] >= start_date) & (df['date'] < end_date)]
    new_measurements_by_month = new_measurements.groupby(new_measurements['date'].dt.month)['id_measurement'].nunique()

    month_names = [calendar.month_name[i] for i in new_measurements_by_month.index]

    new_measurements_by_month_dict = dict(zip(month_names, new_measurements_by_month))

    #total_new_measurements = new_measurements['id_measurement'].nunique()

    return {"new_measurements_by_year": new_measurements_by_month_dict}


@app.get("/wound_status")  # Returns the status of each wound in the dataset
async def get_wound_status():
    df_nonull = df.dropna(subset=['status'])
    wound_status = df_nonull.groupby('id_wound')['status'].first().value_counts().to_dict()
    return {"wound_status": wound_status}


@app.get("/wound_types")  # Returns wound types both primary and secondary
async def get_wound_types():
    df_nonull = df.dropna(subset=['type', 'secondary_type'])
    wound_types = pd.concat([df_nonull.groupby('id_wound')['type'].first(), df_nonull.groupby('id_wound')
    ['secondary_type'].first()]).value_counts().to_dict()
    return {"wound_types": wound_types}


@app.get("/wound_locations")  # Returns wound locations both primary and secondary
async def get_wound_locations():
    df_nonull = df.dropna(subset=['primary_location', 'secondary_location'])
    wound_locations = pd.concat([df_nonull.groupby('id_wound')['primary_location'].first(), df_nonull.groupby
    ('id_wound')['secondary_location'].first()]).value_counts().to_dict()
    return {"wound_locations": wound_locations}


@app.get("/export_data/{endpoint_name}")
async def export_data(endpoint_name: str):
    """
        This endpoint dynamically exports data corresponding to any defined endpoint in CSV format.

        It accepts the name of an existing endpoint as a parameter. The function associated with the given endpoint
        is retrieved and executed to obtain the related data. This data is then converted into CSV format
        and returned as a downloadable file. If the given endpoint name is not associated with any defined function,
        the function returns an error message.

        Parameters:
        endpoint_name (str): The name of the endpoint whose data is to be exported.

        Returns:
        csv_data (str): The requested data in CSV format or an error message if the endpoint name is invalid.
    """
    # Fetch the function from globals
    func = globals().get(endpoint_name)

    # If no function was found for the given endpoint name, return an error
    if not func:
        raise HTTPException(status_code=400, detail="Invalid endpoint name")

    # Call the function to get the data
    data = await func()

    # If the function returns an integer, create a dictionary with appropriate keys
    if isinstance(data, int):
        data = {"total_count": [data]}

    elif isinstance(data, dict):
        for key in data:
            if isinstance(data[key], dict):
                data = data[key]
                break

    try:
        # Convert the data to a DataFrame
        data_df = pd.DataFrame(list(data.items()), columns=["Key", "Value"])

        # Save the DataFrame to a CSV file
        csv_file_path = f"{endpoint_name}_data.csv"
        data_df.to_csv(csv_file_path, index=False)

    except ValueError:
        raise HTTPException(status_code=500, detail="Unable to convert data to a DataFrame")

    # Return the CSV file as a response
    return FileResponse(path=csv_file_path, filename=f"{endpoint_name}_data.csv", media_type="text/csv")


@app.get("/query_search")
async def perform_query_search(query: str, csv_file_path: str = "inSightDataCR_May2020_Koc.csv"):
    try:
        # Perform Query Search By NL
        query_result = prompt.performQuerySearchByNL(query, csv_file_path)

        return {"query_result": query_result}

    except Exception as e:
        return {"error": str(e)}


@app.get("/heatmap_analysis")
async def analyze_heatmap(csv_file_path: str = "inSightDataCR_May2020_Koc.csv"):
    try:
        # Analyse Heatmap
        heatmap_analysis = prompt.analyseHeatmap(csv_file_path)

        return {"heatmap_analysis": heatmap_analysis}

    except Exception as e:
        return {"error": str(e)}


@app.get("/summary_analysis")
async def analyze_summary(csv_file_path: str = "inSightDataCR_May2020_Koc.csv"):
    try:
        # Analyse Summary
        summary_analysis = prompt.analyseSummary(csv_file_path)

        return {"summary_analysis": summary_analysis}

    except Exception as e:
        return {"error": str(e)}


@app.get("/stats_analysis")
async def analyze_stats(csv_file_path: str = "inSightDataCR_May2020_Koc.csv"):
    try:
        # Analyse Stats
        stats_analysis = prompt.analyseStats(csv_file_path)

        return {"stats_analysis": stats_analysis}

    except Exception as e:
        return {"error": str(e)}
