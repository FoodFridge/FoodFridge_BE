import os
from flask import jsonify, request
from flask_restful import Resource
from firebase_admin import auth
import requests
import app
from app.core.firebase import initialize_firebase_app, firestore
import uuid
from dotenv import load_dotenv

class Login_with_email_and_password(Resource):
    def post(self):
        
        try:
            load_dotenv()
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
            print(res.text)


            if status_code == 200:
                res = res.json()

                localId = res['localId'] # localId = uid (uid ใช้ ref data ทั้งหมดเช่น favorite)
                idToken = res['idToken'] # ใช้สำหรับแนบ authorization api เส้นอื่นๆ
                refreshToken = res['refreshToken'] # สำหรับ ขอ token ใหม่กรณี expire ต้องมีเส้น refresh token 
                expiresIn = res['expiresIn'] # เวลา token ที่ใช้ได้

                db = firestore.client()
                collection_ref = db.collection('users')
                docs = collection_ref.where("localId", "==", localId).stream()

                print(docs)

                data = {
                    "localId": localId,
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
        load_dotenv()
        api_key = os.getenv("api_key")

        endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"

        # Assuming you're using JSON data for login credentials
        data = request.get_json()
        # Extract email and password from the request data
        email = data.get('email')
        password = data.get('password')
        # user_id = uuid.uuid4().hex
        name = data.get('name')
        db = firestore.client()

        try:

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



#to do - to verifie email
'''
class Update_Email(Resource):
    def post(self, localId):
        try:
            authorization_header = request.headers.get('Authorization')
            if authorization_header and authorization_header.startswith('Bearer '):
                id_token = authorization_header.split(' ')[1]
            else:
                # Return error response if 'Authorization' header is missing or invalid
                return {"error": "Missing or invalid Authorization header"}, 401

                # Verify the ID token before proceeding
            decoded_token = auth.verify_id_token(id_token)

            if not decoded_token['uid']:
                return {"error": "uid invalid."}, 401

            load_dotenv()
            api_key = os.getenv("api_key")

            endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"

            # Extract email from the request data
            data = request.get_json()
            new_email = data.get('email')

            db = firestore.client()
            collection_ref = db.collection('users')
            query = collection_ref.where('email', '==', new_email)
            docs = query.stream()

            # Check if any documents are returned
            email_exists = any(docs)

            if not email_exists:
                print("Email does not exist in the database. You can proceed to insert the document.")
                if not decoded_token.get('email_verified'):
                    return {"error": "Please verify the new email before changing email"}, 400
                
                auth.update_user(decoded_token['uid'], email=new_email)
                auth.send_email_verification(decoded_token['uid'])
                
                # payload = {
                #     "idToken":id_token,
                #     "email": new_email,
                #     "returnSecureToken": True
                # }

                # response = requests.post(endpoint, json=payload)
                # response_data = response.json()

                return {"message": "Email update requested. Please verify your new email address."}, 200
            else:
                # Email already exists in the database, return an error response
                return {"error": "Email already exists in the database"}, 400

            #     if response.ok:
            #         # Update user's email in Firestore database
            #         user_ref = db.collection('users').document(localId)
            #         user_ref.update({"email": new_email})
            #         return {"message": "Email updated successfully"}, 200
            #     else:
            #         # Return error response if the request to Identity Toolkit API failed
            #         return {"error": response_data.get('error', 'Failed to update email')}, response.status_code
            # else:
            #     # Email already exists in the database, return an error response
            #     return {"error": "Email already exists in the database"}, 400
            
        except Exception as e:
            # Handle any exceptions and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500
'''


class Update_Name(Resource):
    def post(self, localId):
        try:
            authorization_header = request.headers.get('Authorization')
            if authorization_header and authorization_header.startswith('Bearer '):
                id_token = authorization_header.split(' ')[1]
            else:
                # Return error response if 'Authorization' header is missing or invalid
                return {"error": "Missing or invalid Authorization header"}, 401

                # Verify the ID token before proceeding
            decoded_token = auth.verify_id_token(id_token)

            if not decoded_token['uid']:
                return {"error": "uid invalid."}, 401
            
            data = request.get_json()
            new_name = data.get('name')

            db = firestore.client()
            doc_ref = db.collection('users').document(localId)
            print(doc_ref)
            doc_ref.update({"name": new_name})

            response = {
                "status": "success",
                "message": "Document data updated successfully"
            }
            return response, 200

        except Exception as e:
            # Handle exceptions
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500    