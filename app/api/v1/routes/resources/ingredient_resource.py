from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore

class IngredientResource(Resource):
    def get(self):
        try:
            # # Use initialize_firebase_app() in your code
            # initialize_firebase_app()

            db = firestore.client()

            collection_ref = db.collection('ingredient')
            docs = collection_ref.stream()

            data = []
            for doc in docs:
                data.append(doc.to_dict())

            if data:
                # If data is present, return a success response
                response = {
                    "status": "1",
                    "message": "Data retrieved successfully",
                    "data": data
                }
                return response, 200
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

            if data:
                # If data is present, return a success response

                # Filter data based on the condition (alph_val equals "Carb")
                filtered_data = [
                    {"ingredient_id": item.get("ingredient_id"), "ingredient_name": item.get("ingredient_name")}
                    for item in data if item.get("ingredient_type_code") == category
                ]
                
                response = {
                    "status": "1",
                    "message": "Data retrieved successfully",
                    "data": filtered_data
                }
                return response, 200
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



