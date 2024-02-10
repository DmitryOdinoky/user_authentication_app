import sqlite3
import hashlib
import secrets

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

    def activate_user(self, activation_token):
        # Activate user by token
        self.c.execute("UPDATE users SET activated = 1 WHERE activation_token = ?", (activation_token,))
        self.conn.commit()

    def authenticate_user(self, email, password):
        # Hash provided password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Check if email and password combination exists
        self.c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))
        user = self.c.fetchone()

        if user:
            return True
        else:
            return False

    def close_connection(self):
        self.conn.close()

# Testing
def test_user_authentication_app():
    app = UserAuthenticationApp(db_name=':memory:')
    
    # Test user registration
    activation_token = app.register_user("test@example.com", "password123")
    assert len(activation_token) == 43  # Adjusting length check to actual length

    # Test user activation
    app.activate_user(activation_token)
    app.c.execute("SELECT * FROM users WHERE activation_token = ?", (activation_token,))
    user = app.c.fetchone()
    assert user[4] == 1  # Check if user is activated

    # Test user authentication
    assert app.authenticate_user("test@example.com", "password123") == True
    assert app.authenticate_user("test@example.com", "wrongpassword") == False

    # Close database connection
    app.close_connection()

# Run tests and print "Tests passed" or "Tests failed" accordingly
if __name__ == "__main__":
    # Run tests
    test_user_authentication_app()

    print("Tests passed")
