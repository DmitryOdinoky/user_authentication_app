import requests               # Import requests for making HTTP requests
import urllib.parse          # Import urllib.parse for URL encoding and decoding

def register_user(email, password):
    url = 'http://localhost:8000/register'  # URL for registration endpoint
    data = {'email': email, 'password': password}  # Request data with email and password
    try:
        response = requests.post(url, data=data)  # Make a POST request to register user
        if response.status_code == 200:
            activation_url = response.text  # Get activation URL from response
            return activation_url           # Return activation URL on success
        elif response.status_code == 400:
            return "User already registered"  # Return message if user already registered
        else:
            return "Registration failed"      # Return message if registration failed
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"                    # Return error message if request fails

def confirm_registration(email, activation_token):
    url = 'http://localhost:8000/confirm'  # URL for confirmation endpoint
    data = {'email': email, 'activation_token': activation_token}  # Request data with email and activation token
    try:
        response = requests.post(url, data=data)  # Make a POST request to confirm registration
        return response.text                      # Return response text
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"                    # Return error message if request fails

def authenticate_user(email, password):
    url = 'http://localhost:8000/authenticate'  # URL for authentication endpoint
    data = {'email': email, 'password': password}  # Request data with email and password
    try:
        response = requests.post(url, data=data)  # Make a POST request to authenticate user
        if response.status_code == 200:
            return True    # Return True if authentication successful
        else:
            return False   # Return False if authentication failed
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False     # Return False if request fails

# Testing
def test_user_authentication_app():
    email = "test2@example.com"
    password = "password1234"

    # Register user
    activation_url = register_user(email, password)
    print("Activation URL:", activation_url)

    if activation_url == "User already registered":
        print("User already registered")
        return

    # Extract activation token from the URL
    parsed_url = urllib.parse.urlparse(activation_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    activation_token = query_params.get('activation_token', [None])[0]

    # Confirm registration
    confirmation_response = confirm_registration(email, activation_token)
    print("Confirmation response:", confirmation_response)

    # Authenticate user
    authentication_result = authenticate_user(email, password)
    if authentication_result:
        print("Authentication successful")
    else:
        print("Authentication failed")

# Execute the tests
test_user_authentication_app()
