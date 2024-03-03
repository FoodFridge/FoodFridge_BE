                    'localId': localId,
                    'email': email_,
                    'name': email_,
                    # Add other user data as needed
                }

                # Add user data to Firebase Firestore
                db = firestore.client()
                db.collection('users').document(localId).set(user_data)

                token = generate_jwt_token(localId)
                refresh_token = generate_refresh_token(localId)
             
                data = {
                    "localId": localId,
                    "token": token,
                    "refreshToken": refresh_token
                }

                print("data",data)

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
        
