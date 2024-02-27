from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore
from google.cloud.exceptions import NotFound

class IngredientResource(Resource):
    def post(self):
        try:

            data = request.get_json()
            localId = data.get('localId')
            db = firestore.client()
            data = []

            if localId:
                # Check if 'Authorization' header exists
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
                
                collection_ref2 = db.collection('pantry')
                query = collection_ref2.where('user_id', '==', localId)
                docs2 = query.stream()

                for doc in docs2:
                    doc_dict2 = doc.to_dict()

                    pantry = {
                        "user_id": doc_dict2.get("user_id"),
                        "doc_id": doc.id,
                        "ingredient_name": doc_dict2.get("pantryName"),
                        "ingredient_type_code": doc_dict2.get("ingredient_type_code"),
                    }
                    data.append(pantry)
     
            collection_ref = db.collection('ingredient')
            docs = collection_ref.stream()
            
            for doc in docs:
                doc_dict = doc.to_dict()

                # Construct a dictionary to handle optional fields "user_id"
                ingredient = {
                    "user_id": doc_dict.get("user_id", "Not specified"),
                    "doc_id": doc.id,
                    "ingredient_name": doc_dict.get("ingredient_name"),
                    "ingredient_type_code": doc_dict.get("ingredient_type_code"),
                }
                
                data.append(ingredient)

            response = {}
            if data:
                # If data is present, return a success response
                response = {
                    "status": "1",
                    "message": "Data retrieved successfully",
                    "data": data
                }
            else:
                # If no data is present, return a response with a message
                response = {
                    "status": "0",
                    "message": "No data available",
                    "data": []
                }
            return response, 200

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500

    

class IngredientResourceWithCategory(Resource):
    def get(self, category):
        try:
            # # Use initialize_firebase_app() in your code
            # initialize_firebase_app()

            db = firestore.client()

            collection_ref = db.collection('ingredient')
            docs = collection_ref.stream()

            data = []
            for doc in docs:
                data.append(doc.to_dict())

            response = {}
            if data:
                # If data is present, return a success response
                print('data', data)
                # Filter data based on the condition (alph_val equals "Carb")
                filtered_data = [
                    {"ingredient_id": item.get("ingredient_id"), "ingredient_name": item.get("ingredient_name")}
                    for item in data if item.get("ingredient_type_code") == category
                ]
                print('filtered_data', filtered_data)
                response = {
                    "status": "1",
                    "message": "Data retrieved successfully",
                    "data": filtered_data
                }
            else:
                # If no data is present, return a response with a message
                response = {
                    "status": "0",
                    "message": "No data available",
                    "data": []
                }
            return response, 200

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500



class AddIngredients(Resource):
    def post(self):
        try:
            db = firestore.client()
            data = request.get_json()

            ingredient_id = data.get('ingredient_id')
            ingredient_name = data.get('ingredient_name')
            ingredient_type_code = data.get('ingredient_type_code')
            collection_ref = db.collection('ingredient')

            ingredient = {
                'ingredient_id': ingredient_id,
                'ingredient_name': ingredient_name,
                'ingredient_type_code': ingredient_type_code,
            }

            collection_ref.document().set(ingredient)

            return {"success": "added to collection 'Ingredient'"}

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500