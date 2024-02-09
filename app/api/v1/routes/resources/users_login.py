import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

def initialize_firebase():
    # Initialize Firebase app with credentials
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)

def login(email, password):
    try:
        # Sign in the user with email and password
        user = auth.sign_in_with_email_and_password(email, password)
        print("Successfully logged in as:", user['email'])
        return user
    except Exception as e:
        # Handle login errors
        print("Failed to log in:", e)
        return None

# Example usage
if __name__ == "__main__":
    initialize_firebase()
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    user = login(email, password)
    if user:
        # Logged in successfully, proceed with further actions
        pass
    else:
        # Handle login failure
        pass