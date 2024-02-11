import requests
import urllib.parse

def register_user(email, password):
    url = 'http://localhost:8000/register'
    data = {'email': email, 'password': password}
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        activation_url = response.text.replace("<html><body>", "").replace("</body></html>", "")
        return activation_url
    elif response.status_code == 400:
        return "User already registered"
    else:
        return "Registration failed"

def confirm_registration(email, activation_url):
    # Extract activation token from the URL
    parsed_url = urllib.parse.urlparse(activation_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    activation_token = query_params.get('activation_token', [None])[0]

    if not activation_token:
        return "Invalid activation URL"

    # Call the UserAuthenticationApp method to confirm registration
    url = 'http://localhost:8000/confirm'
    data = {'email': email, 'activation_token': activation_token}
    response = requests.post(url, data=data)
    return response.text

def authenticate_user(email, password):
    url = 'http://localhost:8000/authenticate'
    data = {'email': email, 'password': password}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return True
    else:
        return False

# Testing
def test_user_authentication_app():
    email = "test@example.com"
    password = "password123"

    # Register user
    activation_url = register_user(email, password)
    print("Activation URL:", activation_url)

    if activation_url == "User already registered":
        print("User already registered")
        return

    # Confirm registration
    confirmation_response = confirm_registration(email, activation_url)
    print("Confirmation response:", confirmation_response)

    # Authenticate user
    authentication_result = authenticate_user(email, password)
    if authentication_result:
        print("Authentication successful")
    else:
        print("Authentication failed")

# Execute the tests
test_user_authentication_app()
