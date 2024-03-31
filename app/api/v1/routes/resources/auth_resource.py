from flask import request, jsonify
from flask_restful import Resource,reqparse
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore
import requests
from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()
# JWT Secret Key (Should be kept secret)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Authentication parser
auth_parser = reqparse.RequestParser()
auth_parser.add_argument('email', required=True, help='Email is required')
auth_parser.add_argument('password', required=True, help='Password is required')

# Refresh token parser
refresh_token_parser = reqparse.RequestParser()
refresh_token_parser.add_argument('refresh_token', required=True, help='Refresh token is required')

# ตัวแปรข้อมูลแบบ dictionary เก็บ token blacklist
blacklisted_tokens = {}

def messageWithStatusCode(choice):
    def set_message_case1():
        return "An error occurred: Signature verification failed"

    def set_message_case2():
        return "Authorization header missing or Token has expired"

    def set_message_case3():
        return "Authorization header missing or invalid"

    # สร้าง dictionary เพื่อแทนค่า switch-case
    switch = {
        500: set_message_case1,
        401: set_message_case2,
        402: set_message_case3,
    }

    # เลือกฟังก์ชันที่เกี่ยวข้องกับค่า input จาก dictionary และเรียกใช้งาน
    message_func = switch.get(choice, lambda: "Invalid choice")
    return message_func()

def authorization(localId,user_timezone):
    statusCode = ""
    authorization_header = request.headers.get('Authorization')
    if authorization_header and authorization_header.startswith('Bearer '):
        jwt_token = authorization_header.split(' ')[1]
        print("jwt_token",jwt_token)
                    
        db = firestore.client() # init db firebase

        collection_ref = db.collection('token_blacklist')
        query = collection_ref.where('localId', '==', localId).where('token', '==', jwt_token)
        docs = query.stream()


        # Check if any documents are returned
        # data_blacklist = any(docs)
        data_blacklist = is_token_blacklisted(localId,jwt_token)
        print("data_blacklist",data_blacklist)
        if data_blacklist:
            statusCode = 500
           
        
        load_dotenv()
        # JWT Secret Key (Should be kept secret)
        JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        # Verify JWT token
        payload = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=["HS256"])
        
        print("payload",payload)
        # Check token expiration
        # issue timezone
        # if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
            # statusCode = 401
        

        user_timezone = pytz.timezone(user_timezone)

        # Get the current time in the user's timezone
        current_time = datetime.now(user_timezone)

        # Assuming payload['exp'] contains a timestamp in UTC
        exp_timestamp = payload['exp']

        # Convert the expiration timestamp to the user's timezone
        exp_datetime = datetime.fromtimestamp(exp_timestamp, pytz.utc).astimezone(user_timezone)

        # Compare the current time with the expiration datetime
        if current_time > exp_datetime:
            statusCode = 401
    else:
        statusCode = 401
    return statusCode

# Function to generate JWT token with expiration time
def generate_jwt_token(localId):
    # Set token expiration time (e.g., 1 seconds , hours , days)

    load_dotenv()

    EXPIRE_TOKEN = os.getenv("EXPIRE_TOKEN")
    print("EXPIRE_TOKEN",int(EXPIRE_TOKEN))
    expiration_time = datetime.utcnow() + timedelta(seconds=int(EXPIRE_TOKEN))  

    # Create payload with username and expiration time
    payload = {
        'localId': localId,
        'exp': expiration_time
    }

    print("expiration_time",expiration_time)

    # Encode JWT token with secret key
    jwt_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return jwt_token
    # Return JWT token as an array
    # return [jwt_token,expiration_time.isoformat()]

# Function to generate refresh token
def generate_refresh_token(localId):
    return jwt.encode({'localId': localId}, JWT_SECRET_KEY, algorithm='HS256')

# เพิ่ม token ลงใน blacklist พร้อมระบุผู้ใช้
def blacklist_token(user_id, token):
    if user_id in blacklisted_tokens:
        blacklisted_tokens[user_id].add(token)
    else:
        blacklisted_tokens[user_id] = {token}

# ตรวจสอบว่า token ของผู้ใช้ถูกบล็อกหรือไม่
def is_token_blacklisted(user_id, token):
    return user_id in blacklisted_tokens and token in blacklisted_tokens[user_id]

# เมื่อผู้ใช้เข้าสู่ระบบใหม่ ให้เคลียร์ token blacklist ของผู้ใช้
def clear_user_blacklist(user_id):
    if user_id in blacklisted_tokens:
        del blacklisted_tokens[user_id]



# send mail กรณี reset password
def send_email_with_link(sender_email, sender_password, recipient_email, link):
    try:
        # Set up the SMTP server
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(sender_email, sender_password)

        # Create message container
        msg = MIMEMultipart()
        msg['From'] = "FoodFridge"
        msg['To'] = recipient_email
        msg['Subject'] = 'Reset FoodFridge Account Password'

        # Create the body of the message (a simple text with the link)
        body = f'To FoodFridge User,\n\nPlease click this link to reset the password: {link}\n\nBest regards,\nFoodFridge Team'
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        smtp_server.send_message(msg)

        # Close the connection
        smtp_server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print("Failed to send email:", e)

class ResetPasswordResource(Resource):
    def post(self):
        
        try:
            data = request.get_json()
            email = data['email']

            #check email if there is exist in database
            db = firestore.client()
            collection_ref = db.collection('users')
            query = collection_ref.where('email', '==', email)
            docs = query.stream()

            # Check if any documents are returned
            email_exists = any(docs)

            if not email_exists:
                print("Email does not exist in the database. You can proceed to insert the document.")
                response = {
                    "status": "0",
                    "message": "Email not found in the database.",
                }      
                                  
                return response, 404
            
        
            
            #need to change the sender email to foodfridge email
            link = auth.generate_password_reset_link(email)

            # send_email_with_link('peawseaw@gmail.com', 'dkwu cjnb cpil yozh', email, link)

            send_email_with_link('foodfridge.contact@gmail.com', 'coyy xkgu gntn nezb', email, link)


            response = {
                "status": "1",
                "message": "Password reset link sent to the email.",
                }  
            return response, 200
        
        except Exception as e:
            # Handle errors
            print("Failed to reset password:", e)
            return {"message": f"Failed to reset password: {str(e)}"}, 500



# auth email , password
class LoginWithEmailAndPasswordResource(Resource):
    def post(self):
        
        try:
            auth_data = auth_parser.parse_args()
            email = auth_data['email']
            password = auth_data['password']

            load_dotenv()
            api_key = os.getenv("api_key")
            
            
            db = firestore.client()
            collection_ref = db.collection('users')
            docs = collection_ref.where("email", "==", email).stream()
            
            if not any(docs):
                response = {
                    "status": "0",
                    "message": "Email not found. Please check your email address and try again!",
                    "data": []
                }

                return response , 404
                
            else:
         
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
                    # db = firestore.client()
                    # collection_ref = db.collection('users')
                    # docs = collection_ref.where("localId", "==", localId).stream()

                    # print(docs)

                    token = generate_jwt_token(localId)
                    # token = arr[0]
                    # exp = arr[1]
                    refresh_token = generate_refresh_token(localId)


                    # JWT Secret Key (Should be kept secret)
                    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
                    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            
                    clear_user_blacklist(localId)

                    data = {
                        "localId": localId,
                        "token": token,
                        "refreshToken": refresh_token,
                        "expTime": payload['exp']
                    }

                    response = {
                        "status": "1",
                        "message": "Login successful",
                        "data": data
                    }
                    
                    return response , 200
                else:
                    response = {
                    "status": "0",
                    "message": "Incorrect password. Please verify your password and try again!",
                    "data": []
                    }

                    return response , 401

               
        except Exception as e:
            # Handle signup errors
            print("Failed to sign up:", e)
            return {"message": f"Signup failed: {str(e)}"}, 500
      
# logout
class LogoutResource(Resource):
    # ออกจากระบบ
    def post(self):
      
        try:
            data = request.get_json()
            # Extract email and password from the request data
            localId = data.get('localId')
            token = data.get('token')

            if localId == "": # check localId empty
                return {'message': 'Logout successful'}, 200
            
            
            
            blacklist_token(localId,token)
            
            if localId:
                return {'message': 'Logout successful'}, 200
            else:
                return {'error': 'Authorization header missing'}, 400
            
            
            
            # db = firestore.client() # init db firebase

            # collection_ref = db.collection('token_blacklist')
            # query = collection_ref.where('localId', '==', localId).where('token', '==', token)
            # docs = query.stream()

            # # Check if any documents are returned
            # data_exist = any(docs)
            # print("data_exist",data_exist)

            # if not data_exist:
            #     set_data = {
            #         "localId": localId,
            #         'token': token,                        
            #     }

            
            #     # Create a batch object
            #     batch = db.batch()
                
            #     # Reference to the 'favorite' collection
            #     collection_ref = db.collection('token_blacklist')

            #     # Create a new document reference in the batch
            #     document_ref = collection_ref.document()

            #     # Set data for the document in the batch
            #     batch.set(document_ref, set_data)
            #     # Commit the batch
            #     batch.commit()
        
        except Exception as e:
                return {'error': str(e)}, 400


     
    
class RefreshTokenResource(Resource):
    def post(self):
        # Parse refresh token data
        refresh_token_data = refresh_token_parser.parse_args()
        refresh_token = refresh_token_data['refresh_token']

        try:
            # Decode refresh token
            refresh_payload = jwt.decode(
                refresh_token, JWT_SECRET_KEY, algorithms=["HS256"])
            username = refresh_payload['localId']
            print("username",username)
            load_dotenv()
            # Generate new JWT token
            new_jwt_token = generate_jwt_token(username)

            # JWT Secret Key (Should be kept secret)
            # JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
            payload = jwt.decode(new_jwt_token, JWT_SECRET_KEY, algorithms=["HS256"])
            
            return {'message': 'Token refreshed successfully', 'token': new_jwt_token,'expTime':payload['exp']}, 200
        except jwt.ExpiredSignatureError:
            return {'message': 'Refresh token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid refresh token'}, 401


# auth with google
class AuthWithAppResource(Resource):
    # login ด้วย google or apple
    def post(self):
        # idToken = request.json.get('idToken')
        email_ = request.json.get('email')
        localId = request.json.get('localId')
 
        try:
            # print("idToken",idToken)
            # Verify ID token
            # decoded_token = auth.verify_id_token(idToken)
            # localId = decoded_token['uid']
            # print("localId",localId)
            
            db = firestore.client()
            collection_ref = db.collection('users')
            # check data users from uid
            docs = collection_ref.where("localId", "==", localId).stream()
            
            # check data in docs
            if any(docs):
                token = generate_jwt_token(localId)
                refresh_token = generate_refresh_token(localId)

                # JWT Secret Key (Should be kept secret)
                JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
                
                # clear_user_blacklist(localId)

                data = {
                    "localId": localId,
                    "token": token,
                    "refreshToken": refresh_token,
                    "expTime": payload['exp']
                }
                    
                response = {
                "status": "1",
                "message": "Authen successful",
                "data": data
                }
            else:
                # กรณียังไม่มี localId ให้ insert ลง users
                user_data = {
                    'localId': localId,
                    'email': email_,
                    'name': email_,
                }

                # Add user data to Firebase Firestore
                db = firestore.client()
                db.collection('users').document(localId).set(user_data)

                token = generate_jwt_token(localId)
                refresh_token = generate_refresh_token(localId)
                
                JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
             
                data = {
                    "localId": localId,
                    "token": token,
                    "refreshToken": refresh_token,
                    "expTime": payload['exp']
                }

                # print("data",data)

                response = {
                "status": "1",
                "message": "Auth & Register successful",
                "data": data
                }

            return response , 200
        except Exception as e:
            return {'error': str(e)}, 400



# signup with email , password
class SignupWithEmailAndPasswordResource(Resource):
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
                
                return response , 200
            else:
                response = {
                    "status": "0",
                    "message": "Email already exists!",
                }   
                                  
                return response, 409 
        
        except Exception as e:
            # Handle signup errors
            print("Failed to sign up:", e)
            return {"message": f"Signup failed: {str(e)}"}, 500
        


class UpdateProfileResource(Resource):
    def post(self):
        try:
          
            data = request.get_json()
            new_name = data.get('name')
            localId = data.get('localId')

            code = authorization(localId)
            print("code",code)
            if code != "":
                message = messageWithStatusCode(code)
                return {'message': message},code

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


# update password
class UpdatePasswordResource(Resource):
    def post(self):
        try:
            # Get new password from request data
            data = request.get_json()
            new_password = data.get('password')
            localId = data.get('localId')

            code = authorization(localId)
            print("code",code)
            if code != "":
                message = messageWithStatusCode(code)
                return {'message': message},code

            # Update password using Firebase Authentication
            user = auth.update_user(localId, password=new_password)

            # Return success response
            return {"message": "Password updated successfully"}, 200

        except Exception as e:
            # Return error response if any exception occurs
            return {"error": str(e)}, 500
        
