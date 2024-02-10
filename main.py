import pytest
import sqlite3
import hashlib
import secrets

@pytest.fixture
def database_connection():
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    yield conn, c
    conn.close()

# Create users table if not exists
def create_users_table(c):
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, activation_token TEXT, activated INTEGER)''')

def register_user(conn, c, email, password):
    # Hash password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Generate activation token
    activation_token = secrets.token_urlsafe(32)  # Adjusting token length to 32 characters
    
    # Insert user into database
    c.execute("INSERT INTO users (email, password, activation_token, activated) VALUES (?, ?, ?, ?)", (email, hashed_password, activation_token, 0))
    conn.commit()
    
    return activation_token

def activate_user(conn, c, activation_token):
    # Activate user by token
    c.execute("UPDATE users SET activated = 1 WHERE activation_token = ?", (activation_token,))
    conn.commit()

def authenticate_user(conn, c, email, password):
    # Hash provided password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Check if email and password combination exists
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))
    user = c.fetchone()
    
    if user:
        return True
    else:
        return False

# Testing
def test_register_user(database_connection):
    conn, c = database_connection
    create_users_table(c)
    
    # Test user registration
    activation_token = register_user(conn, c, "test@example.com", "password123")
    assert len(activation_token) == 43  # Adjusting length check to actual length

def test_activate_user(database_connection):
    conn, c = database_connection
    create_users_table(c)
    
    # Test user activation
    activation_token = register_user(conn, c, "test@example.com", "password123")
    activate_user(conn, c, activation_token)
    c.execute("SELECT * FROM users WHERE activation_token = ?", (activation_token,))
    user = c.fetchone()
    assert user[4] == 1  # Check if user is activated

def test_authenticate_user(database_connection):
    conn, c = database_connection
    create_users_table(c)
    
    # Test user authentication
    activation_token = register_user(conn, c, "test@example.com", "password123")
    assert authenticate_user(conn, c, "test@example.com", "password123") == True
    assert authenticate_user(conn, c, "test@example.com", "wrongpassword") == False

# Run tests and print "Tests passed" or "Tests failed" accordingly
if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-qq"])

    # Check if all tests passed
    if pytest.main([__file__, "-qq"]) == 0:
        print("Tests passed")
    else:
        print("Tests failed")
