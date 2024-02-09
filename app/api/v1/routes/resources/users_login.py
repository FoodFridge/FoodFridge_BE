import firebase_admin
from flask import Response, jsonify, request
from flask_restful import Resource, reqparse
from app.core.firebase import initialize_firebase_app, firestore
from firebase_admin import auth
import uuid
# import pyrebase
# from urllib3.exceptions import InsecureRequestWarning



# firebaseConfig = {
#                 'apiKey': "AIzaSyBq5lsZOZoMmhdMMI2CLJsLxwH-QpEwirk",
#                 'authDomain': "foodfridge-617b1.firebaseapp.com",
#                 'databaseURL': "https://foodfridge-617b1-default-rtdb.firebaseio.com",
#                 'projectId': "foodfridge-617b1",
#                 'storageBucket': "foodfridge-617b1.appspot.com",
#                 'messagingSenderId': "664643258545",
#                 'appId': "1:664643258545:web:04a8b0d3c6a856a5737a90",
#                 'measurementId': "G-1XF57EL9ES"
# }

# firebase=pyrebase.initialize_app(firebaseConfig)
# auth=firebase.auth()

# def initialize_firebase():
#     # Initialize Firebase app with credentials
#     cred = credentials.Certificate("firebase_credentials.json")
#     firebase_admin.initialize_app(cred)

# def login(email, password):
#     try:
#         # Sign in the user with email and password
#         user = auth.sign_in_with_email_and_password(email, password)
#         print("Successfully logged in as:", user['email'])
#         return user
#     except Exception as e:
#         # Handle login errors
#         print("Failed to log in:", e)
#         return None

# def verify_token(id_token):
#     try:
#         decoded_token = auth.verify_id_token(id_token)
#         # Token is valid, extract user info from decoded_token
#         return decoded_token
#     except auth.InvalidIdTokenError:
#         # Handle invalid token
#         return None

def custom_authentication(email, password):
    # Perform authentication logic (e.g., validate credentials, retrieve user data, etc.)
    # Example:
    if email == 'user@example.com' and password == 'password':
        # Dummy authentication logic for demonstration
        user_id = '123456789'
        return user_id
    else:
        return None


class Login(Resource):
    def post(self):
        # Assuming you're using JSON data for login credentials
        data = request.get_json()
        # Extract email and password from the request data
        email = data.get('email')
        password = data.get('password')

        

        db = firebase.database()
        if not email or not password:
            return {"message": "Email and password are required"}, 400

        try:
            # Attempt to sign in the user with email and password
            # user = auth.get_user_by_email(email)
            user = auth.sign_in_with_email_and_password(email, password)
            print("Successfully logged in as:", user.email)
                # Handle successful login
            # Get the user's UID
            uid = user['localId']

            db.child("users").child(uid).set(data)

            return {"message": "Login successful", "email": user.email}, 200

        except auth.UserNotFoundError:
            # Handle user not found error
            return {"message": "User not found"}, 404
        except auth.InvalidPasswordError:
            print("Invalid password for user:", email)
            return None
        except auth.AuthError as e:
            print("Error authenticating user:", e)
            return None
        
class Logout(Resource):
    def post(self):
        # Perform logout logic here
        # This can include invalidating session tokens, clearing cookies, etc.
        
        # Example: Clear session token
        # session.clear()  # Assuming you're using Flask-Session
        
        return {"message": "Logout successful"}, 200
    
class Signup(Resource):
    def post(self):
        # Parse request data
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='Email address is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        parser.add_argument('name', type=str, required=True, help='Name is required')
        args = parser.parse_args()
        
        # Extract email and password from the request data
        email = args['email']
        password = args['password']
        name = args['name']
        user_id = uuid.uuid4().hex
        db = firestore.client()

        try:
            # Check if the password meets the requirements
            if len(password) < 6:
                raise ValueError("Password must be at least 6 characters long")
            
            # Create the user with email and password using Firebase Authentication
            user = auth.create_user(email=email, password=password)
            print("Successfully signed up as:", user.email)

            user_ref = db.collection('users').document()
            user_ref.set({
                'email': email,
                'name': name,
                'user_id': user_id
                # Add more user data fields as needed
            })
            return {"message": "Signup successful", "email": user.email}, 201
        except Exception as e:
            # Handle signup errors
            print("Failed to sign up:", e)
            return {"message": f"Signup failed: {str(e)}"}, 500
        
# # Example usage
# if __name__ == "__main__":
#     initialize_firebase()
#     email = input("Enter your email: ")
#     password = input("Enter your password: ")
#     user = login(email, password)
#     if user:
#         # Logged in successfully, proceed with further actions
#         pass
#     else:
#         # Handle login failure
#         pass