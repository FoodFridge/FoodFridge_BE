import os
from flask import jsonify, request, session
from flask_restful import Resource
import requests
import app
from app.core.firebase import initialize_firebase_app, firestore
import uuid


class Login_up_with_email_and_password(Resource):
    def post(self):

        try:
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

            res = requests.post(endpoint, json=data)
            status_code = res.status_code

            if status_code == 200:
                res = res.json()

                id = res['localId'] # localId = uid (uid ใช้ ref data ทั้งหมดเช่น favorite)
                idToken = res['idToken'] # ใช้สำหรับแนบ authorization api เส้นอื่นๆ
                refreshToken = res['refreshToken'] # สำหรับ ขอ token ใหม่กรณี expire ต้องมีเส้น refresh token 
                expiresIn = res['expiresIn'] # เวลา token ที่ใช้ได้

                data = {
                    "id": id,
                    "token": idToken,
                    "refreshToken": refreshToken,
                    "expiresIn": expiresIn
                }

                response = {
                    "status": "1",
                    "message": "Authentication successful. Welcome "+email,
                    "data": data
                }
            else:
                response = {
                    "status": "0",
                    "message": "Invalid Email or Password!",
                    "data": []
                }

            return response , 200
        except Exception as e:
            # Handle signup errors
            print("Failed to sign up:", e)
            return {"message": f"Signup failed: {str(e)}"}, 500
      


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

            # db = firestore.client()
            collection_ref = db.collection('users')
            query = collection_ref.where('email', '==', email)
            docs = query.stream()

            # Check if any documents are returned
            email_exists = any(docs)

            if not email_exists:
                print("Email does not exist in the database. You can proceed to insert the document.")
         
                # Check if the password meets the requirements
                if len(password) < 6:
                    raise ValueError("Password must be at least 6 characters long")

                data = {
                    "email": email,
                    "password": password,
                    "returnSecureToken": True
                }

                # Send POST request
                response = requests.post(endpoint, json=data)

                # localId = uid
                localId =  response.json().get("localId")

                # set uid = document id
                user_ref = db.collection('users').document(localId)
                user_ref.set({
                    'email': email,
                    'name': name,
                    'user_id': user_id
                })

                response = {
                    "status": "1",
                    "message": "Data retrieved successfully",
                }   
            else:
                response = {
                    "status": "0",
                    "message": "Data already exists",
                }   
            
            return response , 200
        
        except Exception as e:
            # Handle signup errors
            print("Failed to sign up:", e)
            return {"message": f"Signup failed: {str(e)}"}, 500
        

class Logout(Resource):
    def post(self):
        # session.clear()
        print('sign out successfull')
            # Check if the request was successful
        return 'sign out successfull'
