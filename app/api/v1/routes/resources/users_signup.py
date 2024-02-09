import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

def initialize_firebase():
    # Initialize Firebase app with credentials
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)

def signup(email, password):
    try:
        # Create a new user with email and password
        user = auth.create_user_with_email_and_password(email, password)
        print("Successfully signed up as:", user.email)
        return user
    except Exception as e:
        # Handle signup errors
        print("Failed to sign up:", e)
        return None

# Example usage
if __name__ == "__main__":
    initialize_firebase()
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    confirm_password = input("Confirm your password: ")
    if password == confirm_password:
        user = signup(email, password)
        if user:
            # Signup successful, proceed with further actions
            pass
        else:
            # Handle signup failure
            pass
    else:
        print("Passwords do not match.")