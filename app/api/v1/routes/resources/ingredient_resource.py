from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore
from google.cloud.exceptions import NotFound

class IngredientResource(Resource):
    def get(self, user_id):
        try:
            # # Use initialize_firebase_app() in your code
            # initialize_firebase_app()

            db = firestore.client()

            collection_ref = db.collection('ingredient')
            collection_ref2 = db.collection('pantry')

            # Construct the query
            query = collection_ref2.where('user_id', '==', user_id)

            docs = collection_ref.stream()
            docs2 = query.stream()

            

            data = []
            for doc in docs:
                doc_dict = doc.to_dict()

                # Construct a dictionary to handle optional fields "user_id"
                ingredient = {
                    "user_id": doc_dict.get("user_id", "Not specified"),
                    "ingredient_id": doc_dict.get("ingredient_id"),
                    "ingredient_name": doc_dict.get("ingredient_name"),
                    "ingredient_type_code": doc_dict.get("ingredient_type_code"),
                }
                
                data.append(ingredient)

            for doc in docs2:
                doc_dict2 = doc.to_dict()
                pantrie = {
                    "user_id": doc_dict2.get("user_id"),
                    "ingredient_id": doc_dict2.get("pantry_id"),
                    "ingredient_name": doc_dict2.get("pantryName"),
                    "ingredient_type_code": doc_dict2.get("ingredient_type_code"),
                }
                data.append(pantrie)

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



