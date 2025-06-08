from flask import Flask, request, redirect, session
import json, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '91e58445d99521b68ca9965737c54351'  # Use secrets.token_hex(16)
USER_FILE = 'users.json'

# Load users safely
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# Save users
def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# Home -> redirect to login
@app.route('/')
def home():
    return redirect('/login')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        users = load_users()

        if username in users:
            return error_page("Username already exists. Try login.")

        users[username] = generate_password_hash(password)
        save_users(users)
        return success_page("Signup successful. You can now login.", "/login")

    return html_page("Signup", '''
        <form method="POST">
            <input name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Signup</button>
        </form>
        <p>Already have an account? <a href="/login">Login</a></p>
    ''')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        users = load_users()

        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            return redirect('/dashboard')
        return error_page("Invalid username or password.")

    return html_page("Login", '''
        <form method="POST">
            <input name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Login</button>
        </form>
        <p>Don't have an account? <a href="/signup">Signup</a></p>
    ''')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    return html_page("Dashboard", f'''
        <h2>Welcome, {session["username"].title()}!</h2>
        <a href="/logout">Logout</a>
    ''')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return success_page("Logged out successfully.", "/login")

# Base HTML template
def html_page(title, body):
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial; background: #f2f2f2; padding: 40px; }}
            form {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px #ccc; width: 300px; margin: auto; }}
            input {{ width: 100%; padding: 10px; margin: 10px 0; }}
            button {{ padding: 10px; background: #007BFF; color: white; border: none; width: 100%; }}
            a {{ text-decoration: none; color: #007BFF; }}
            h2 {{ text-align: center; }}
            p {{ text-align: center; }}
        </style>
    </head>
    <body>
        <h2>{title}</h2>
        {body}
    </body>
    </html>
    '''

# Success / Error message page
def success_page(message, link='/'):
    return html_page("Success", f"<p>{message}</p><p><a href='{link}'>Continue</a></p>")

def error_page(message):
    return html_page("Error", f"<p style='color:red'>{message}</p><p><a href='javascript:history.back()'>Go Back</a></p>")

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)