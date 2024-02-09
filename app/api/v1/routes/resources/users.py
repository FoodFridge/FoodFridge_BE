import os
from flask import jsonify, request
from flask_restful import Resource
import requests
from app.core.firebase import initialize_firebase_app, firestore
import uuid


active_sessions = set()

class Login_up_with_email_and_password(Resource):
    def post(self):
        api_key = os.getenv("api_key")
        
        endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        # Assuming you're using JSON data for login credentials
        data = request.get_json()
        # Extract email and password from the request data
        email = data.get('email')
        password = data.get('password')

        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        

        # Send POST request
        response = requests.post(endpoint, json=data)
        idToken =  response.json().get("idToken")

        if idToken not in active_sessions:
            active_sessions.add(idToken)

        # print('session', active_sessions)

        if response.status_code == 200:
            # Request successful, parse and return response JSON
            return response.json()
        else:
            # Request failed, print error message
            error_message = response.json().get('error', 'Failed to sign in')
            print(f"Failed to sign in: {error_message}")
            return None
        
class Logout(Resource):
    def post(self):

        data = request.get_json()

        idToken = data.get('idToken')
        print('sessio',active_sessions)
        print('id',idToken)
        # Firebase Authentication REST API endpoint for revoking tokens
        if idToken in active_sessions:
        # Invalidate the session or token
            active_sessions.remove(idToken)
            print('sign out successfull')
            # Check if the request was successful
            return 'sign out successfull'
        else:
            # Token revocation failed, return error response
            print(f"Failed to sign out")
            return "Failed to sign out"


class Sign_up_with_email_and_password(Resource):
    def post(self):
        api_key = os.getenv("api_key")

        endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"

        # Assuming you're using JSON data for login credentials
        data = request.get_json()
        # Extract email and password from the request data
        email = data.get('email')
        password = data.get('password')
        user_id = uuid.uuid4().hex
        name = data.get('name')
        db = firestore.client()

        try:
#             # Check if the password meets the requirements
            if len(password) < 6:
                raise ValueError("Password must be at least 6 characters long")

            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }

            # Send POST request
            response = requests.post(endpoint, json=data)
            
            data = response.json()

            idToken = data.get('idToken')
            print(data.get('idToken'))

            if idToken not in active_sessions:
                active_sessions.add(idToken)
            
            user_ref = db.collection('users').document()
            user_ref.set({
                'email': email,
                'name': name,
                'user_id': user_id
                # Add more user data fields as needed
            })

            if response.status_code == 200:
                # Request successful, parse and return response JSON
                return response.json()
            else:
                # Request failed, print error message
                print(f"Failed to sign up: {response.json()}")
                return None
        
        except Exception as e:
            # Handle signup errors
            print("Failed to sign up:", e)
            return {"message": f"Signup failed: {str(e)}"}, 500