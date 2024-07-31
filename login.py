from flask import Flask, request, redirect, url_for, render_template_string, session
import pandas as pd
import socket
from google.cloud import bigquery
from google.oauth2 import service_account

# Flask setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for session management

# Google Cloud and BigQuery setup
credentials = service_account.Credentials.from_service_account_file('path_to_your_service_account_file.json')
project_id = 'your_project_id'
client = bigquery.Client(credentials=credentials, project=project_id)

# Static ID and password
USERNAME = 'admin'
PASSWORD = 'password123'

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return 'Invalid credentials', 401
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f9f9f9;
            margin: 0;
        }
        .login-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 300px;
        }
        .login-container h2 {
            margin-bottom: 20px;
        }
        .login-container input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .login-container button {
            width: 100%;
            padding: 10px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .login-container button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Login</h2>
        <form method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
    """)

# Home Route
@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Your existing home route code
    # ...

# Rest of your existing code
# ...

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5000)
