import sqlite3                  # Import SQLite3 for database operations
import hashlib                  # Import hashlib for hashing passwords
import secrets                  # Import secrets for generating secure tokens
import urllib.parse             # Import urllib.parse for URL encoding and decoding
from http.server import BaseHTTPRequestHandler, HTTPServer  # Import BaseHTTPRequestHandler and HTTPServer for handling HTTP requests

class UserAuthenticationApp:
    def __init__(self, db_name='users.db'):
        # Initialize the UserAuthenticationApp class with a SQLite database connection
        self.conn = sqlite3.connect(db_name)  # Connect to the SQLite database
        self.c = self.conn.cursor()           # Create a cursor to execute SQLite commands
        self.create_users_table()             # Call the method to create the users table in the database

    def create_users_table(self):
        # Create the users table if it doesn't exist
        self.c.execute('''CREATE TABLE IF NOT EXISTS users
                          (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, activation_token TEXT, activated INTEGER)''')
        self.conn.commit()  # Commit the transaction to save changes to the database

    def register_user(self, email, password):
        # Check if the user already exists
        if self.user_exists(email):
            return "User already registered"  # Return message if user already exists

        # Hash the password using SHA-256
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Generate a secure activation token
        activation_token = secrets.token_urlsafe(32)

        # Insert user data into the database
        self.c.execute("INSERT INTO users (email, password, activation_token, activated) VALUES (?, ?, ?, ?)",
                       (email, hashed_password, activation_token, 0))
        self.conn.commit()  # Commit the transaction to save changes to the database

        return activation_token  # Return the activation token

    def confirm_registration(self, email, activation_token):
        # Verify activation token and activate user
        self.c.execute("UPDATE users SET activated = 1 WHERE email = ? AND activation_token = ?",
                       (email, activation_token))
        self.conn.commit()  # Commit the transaction to save changes to the database

    def generate_activation_url(self, email, activation_token):
        # Generate activation URL with email and activation token
        params = {'email': email, 'activation_token': activation_token}
        encoded_params = urllib.parse.urlencode(params)
        activation_url = f"http://example.com/activate?{encoded_params}"
        return activation_url  # Return the activation URL

    def authenticate_user(self, email, password):
        # Hash provided password using SHA-256
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Check if email and password combination exists and user is activated
        self.c.execute("SELECT * FROM users WHERE email = ? AND password = ? AND activated = 1",
                       (email, hashed_password))
        user = self.c.fetchone()

        if user:
            return True  # Return True if authentication successful
        else:
            return False  # Return False if authentication failed

    def close_connection(self):
        self.conn.close()  # Close the database connection

    def user_exists(self, email):
        # Check if user with given email exists in the database
        self.c.execute("SELECT * FROM users WHERE email = ?", (email,))
        return self.c.fetchone() is not None  # Return True if user exists, False otherwise

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Handle POST requests
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')  # Read request data
        data = urllib.parse.parse_qs(post_data)  # Parse POST data into a dictionary
        email = data.get('email', [None])[0]     # Extract email from POST data
        password = data.get('password', [None])[0]  # Extract password from POST data
        activation_token = data.get('activation_token', [None])[0]  # Extract activation token from POST data

        if self.path == '/register':
            # Handle registration request
            if email and password:
                # If email and password provided, register the user
                activation_token = app.register_user(email, password)
                activation_url = app.generate_activation_url(email, activation_token)
                # Generate activation URL and send it as response
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(activation_url.encode('utf-8'))
            else:
                # If email or password is missing, send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write("Missing email or password".encode('utf-8'))

        elif self.path == '/confirm':
            # Handle confirmation request
            if email and activation_token:
                # If email and activation token provided, confirm registration
                app.confirm_registration(email, activation_token)
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write("User activated successfully".encode('utf-8'))
            else:
                # If email or activation token is missing, send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write("Missing email or activation token".encode('utf-8'))

        elif self.path == '/authenticate':
            # Handle authentication request
            if email and password:
                # If email and password provided, authenticate the user
                authenticated = app.authenticate_user(email, password)
                if authenticated:
                    # If authentication successful, send success response
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                else:
                    # If authentication failed, send error response
                    self.send_response(401)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
            else:
                # If email or password is missing, send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()

def run_server(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    # Run the HTTP server
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    try:
        httpd.serve_forever()  # Start serving requests indefinitely
    except KeyboardInterrupt:
        print('Stopping server...')
        httpd.server_close()   # Close the server when interrupted by KeyboardInterrupt

if __name__ == '__main__':
    app = UserAuthenticationApp()  # Create an instance of UserAuthenticationApp
    run_server()                    # Run the HTTP server
