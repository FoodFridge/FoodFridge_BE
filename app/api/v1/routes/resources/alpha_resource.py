from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore

class AlphaResource(Resource):
    def get(self, type):
        try:
            # # Use initialize_firebase_app() in your code
            # initialize_firebase_app()

            db = firestore.client()

            collection_ref = db.collection('alpha')
            docs = collection_ref.stream()

            data = []
            for doc in docs:
                data.append(doc.to_dict())

            if data:
                # If data is present, return a success response

                # Filter data based on the condition (alph_val equals "Carb")
                # filtered_data = [item for item in data if item.get("alph_type") == type]
                filtered_data = [
                    {"code": item.get("alph_code"), "name": item.get("alph_val"), "sort": item.get("alph_seq")}
                    for item in data if item.get("alph_type") == type
                ]
                
                # Convert "sort" values to integers before sorting
                for item in filtered_data:
                    item["sort"] = int(item["sort"])

                # Sort data based on the "sort" field
                sorted_data = sorted(filtered_data, key=lambda x: x["sort"])


                response = {
                    "status": "1",
                    "message": "Data retrieved successfully",
                    "data": sorted_data
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
