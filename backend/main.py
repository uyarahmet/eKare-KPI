from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import sqlite3

from starlette.responses import RedirectResponse

app = FastAPI()


# Define a function to create database connection
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('users.db')
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


# Define a function to insert a user into the table
def insert_user(conn, username, password):
    try:
        conn.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}');")
        conn.commit()
        print(f"User {username} inserted successfully")
    except sqlite3.Error as e:
        print(e)


# Define a function to authenticate user
def authenticate_user(conn, username, password):
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}';")
        user = cur.fetchone()
        if user:
            print(f"User {username} authenticated successfully")
            return True
        else:
            print(f"User {username} authentication failed")
            return False
    except sqlite3.Error as e:
        print(e)
        return False


# Define a route for the login page
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
            <form method="post" action="/login">
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
        </body>
    </html>
    """


# Define a route to handle login request
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    conn = create_connection()
    create_user_table(conn)
    authenticated = authenticate_user(conn, username, password)
    conn.close()
    if authenticated:
        return {"message": "Login successful"}
    else:
        return {"message": "Login failed"}


@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...)):
    conn = create_connection()
    create_user_table(conn)
    # Check if the username already exists
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE username='{username}';")
    user = cur.fetchone()

    if user:

        return {"message": "user already exists"}
    else:
        insert_user(conn, username, password)
        return {"message": "succesful"}

    #if user:
    #    conn.close()
    # Redirect the user back to the sign-up page with an error message
    #     return RedirectResponse("/signup?error=username_exists")
    #else:
    #
    #    conn.close()
    # Redirect the user back to the login page with a success message


    #   return RedirectResponse("/login?message=signup_success")