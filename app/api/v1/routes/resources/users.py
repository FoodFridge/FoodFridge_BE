import os
from flask import jsonify, request
from flask_restful import Resource
import requests
from app.core.firebase import initialize_firebase_app, firestore

from firebase_admin import auth
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
                    'localId': localId,
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

        # headers = request.headers

        # # Create a new dictionary without the 'Authorization' key
        # new_headers = {key: value for key, value in headers.items() if key != 'Authorization'}

        # # Create a new EnvironHeaders object with the updated headers
        # request.headers = new_headers

        # return {'message': 'Logout successful'}, 200


        # Get the Firebase ID token from the Authorization header
        id_token = request.headers.get('Authorization')

        #print("id_token : ",id_token)

        if id_token:
            try:
                # Verify and decode the Firebase ID token
                decoded_token = auth.verify_id_token(id_token)
                # Get the user's UID from the decoded token
                uid = decoded_token['uid']
                # Revoke the user's session
                auth.revoke_refresh_tokens(uid)
                return {'message': 'Logout successful'}, 200
            except auth.InvalidIdTokenError:
                return {'error': 'Invalid ID token'}, 401
            except auth.RevocationError:
                return {'error': 'Error revoking tokens'}, 500
            except Exception as e:
                return {'error': str(e)}, 500
        else:
            return {'error': 'Authorization header missing'}, 400
    

class LoginWithGoogle(Resource):
    def post(self):
        id_token = request.json.get('idToken')

        try:
            # Verify ID token
            decoded_token = auth.verify_id_token(id_token)
            # print("decoded_token",decoded_token)
            uid = decoded_token['uid']
            email = decoded_token['email']
            token = id_token
            refreshToken = ''
            # Expiration time
            expiresIn = decoded_token['exp']
            
            # return
            db = firestore.client()
            collection_ref = db.collection('users')
            docs = collection_ref.where("localId", "==", uid).stream()

            # print(docs)

            if any(docs):
                data = {
                    "localId": uid,
                    "token": token,
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
            return {'error': str(e)}, 400



class SignUpWithGoogle(Resource):
    def post(self):
        id_token = request.json.get('idToken')

        try:
            # Verify ID token
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            
            # Check if user with this uid already exists
            existing_user = auth.get_user(uid)

            if existing_user:
                # User already exists, return an error
                return {'error': 'User already registered'}, 400
            
            # Extract user data
            user_data = {
                'uid': uid,
                'email': decoded_token['email'],
                'name': decoded_token.get('name', ''),
                # Add other user data as needed
            }

            # Add user data to Firebase Firestore
            db = firestore.client()
            db.collection('users').document(uid).set(user_data)

            # Create custom token for authentication
            custom_token = auth.create_custom_token(uid)

            # Return response with custom token
            return {'message': 'User registered successfully', 'customToken': custom_token.decode()}, 200
        except auth.InvalidIdTokenError:
            return {'error': 'Invalid ID token'}, 400
        except Exception as e:
            return {'error': str(e)}, 400
        
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



class Update_Password(Resource):
    def post(self):
        try:
            # Get Authorization header
            authorization_header = request.headers.get('Authorization')
            if authorization_header and authorization_header.startswith('Bearer '):
                id_token = authorization_header.split(' ')[1]
            else:
                # Return error response if 'Authorization' header is missing or invalid
                return {"error": "Missing or invalid Authorization header"}, 401

            # Verify the ID token before proceeding
            decoded_token = auth.verify_id_token(id_token)
            if not decoded_token['uid']:
                return {"error": "Invalid uid in token"}, 401

            # Get new password from request data
            data = request.get_json()
            new_password = data.get('password')

            # Update password using Firebase Authentication
            user = auth.update_user(decoded_token['uid'], password=new_password)

            # Return success response
            return {"message": "Password updated successfully"}, 200

        except Exception as e:
            # Return error response if any exception occurs
            return {"error": str(e)}, 500