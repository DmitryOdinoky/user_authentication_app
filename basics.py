import sqlite3
import hashlib
import secrets
import urllib.parse

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

# Testing
def test_user_authentication_app():
    app = UserAuthenticationApp(db_name=':memory:')
    all_tests_passed = True
    
    # Test registration API
    activation_url = app.simulate_registration_api("test@example.com", "password123")
    print("Activation URL:", activation_url)

    # Test confirmation API
    activation_token = activation_url.split('=')[1]
    app.simulate_confirmation_api("test@example.com", activation_token)
    app.c.execute("SELECT * FROM users WHERE email = ?", ("test@example.com",))
    user = app.c.fetchone()
    if user[4] != 1:
        all_tests_passed = False

    # Test authentication API
    if not app.simulate_authentication_api("test@example.com", "password123"):
        all_tests_passed = False
    if app.simulate_authentication_api("test@example.com", "wrongpassword"):
        all_tests_passed = False

    # Close database connection
    app.close_connection()

    return all_tests_passed




testing = test_user_authentication_app()
# Execute the tests
if testing:
    print("Tests passed")