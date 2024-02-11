import sqlite3
import hashlib
import secrets
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

class UserAuthenticationApp:
    def __init__(self, db_name=':memory:'):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.create_users_table()

    def create_users_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS users
                          (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, activation_token TEXT, activated INTEGER)''')
        self.conn.commit()


    def register_user(self, email, password):
        # Check if the user already exists
        if user_exists(email):
            return "User already registered"

        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Generate activation token
        activation_token = secrets.token_urlsafe(32)

        # Insert user into database
        self.c.execute("INSERT INTO users (email, password, activation_token, activated) VALUES (?, ?, ?, ?)", (email, hashed_password, activation_token, 0))
        self.conn.commit()

        return activation_token

    def confirm_registration(self, email, activation_token):
        # Verify activation token and activate user
        self.c.execute("UPDATE users SET activated = 1 WHERE email = ? AND activation_token = ?", (email, activation_token))
        self.conn.commit()

    def generate_activation_url(self, email, activation_token):
        # Generate activation URL
        params = {'email': email, 'activation_token': activation_token}
        encoded_params = urllib.parse.urlencode(params)
        activation_url = f"http://example.com/activate?{encoded_params}"
        return activation_url

    def authenticate_user(self, email, password):
        # Hash provided password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Check if email and password combination exists and user is activated
        self.c.execute("SELECT * FROM users WHERE email = ? AND password = ? AND activated = 1", (email, hashed_password))
        user = self.c.fetchone()

        if user:
            return True
        else:
            return False

    def close_connection(self):
        self.conn.close()

    def simulate_registration_api(self, email, password):
        # Simulate registration API request
        activation_token = self.register_user(email, password)
        activation_url = self.generate_activation_url(email, activation_token)
        return activation_url

    def simulate_confirmation_api(self, email, activation_token):
        # Simulate confirmation API request
        self.confirm_registration(email, activation_token)

    def simulate_authentication_api(self, email, password):
        # Simulate authentication API request
        return self.authenticate_user(email, password)

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = urllib.parse.parse_qs(post_data)
        email = data.get('email', [None])[0]
        password = data.get('password', [None])[0]
        
        if email and password:
            activation_url = app.simulate_registration_api(email, password)
            activation_url = activation_url.replace("<html><body>", "").replace("</body></html>", "")
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(activation_url.encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("Missing email or password".encode('utf-8'))

def user_exists(email):
    app.c.execute("SELECT * FROM users WHERE email = ?", (email,))
    return app.c.fetchone() is not None

def run_server(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    app = UserAuthenticationApp()
    run_server()
