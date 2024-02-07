import json
from flask import Flask, request, jsonify
from flask_restful import Resource
from app.core.firebase import initialize_firebase_app, firestore
from datetime import datetime
import logging
# from google.cloud.firestore_v1 import DatetimeWithNanoseconds

app = Flask(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

class PantryResourceByUser(Resource):
    def get(self, user_id):
        try:
            db = firestore.Client()
            collection_ref = db.collection('pantry')
            docs = collection_ref.stream()

            data = []
            for doc in docs:
                doc_data = doc.to_dict()
                if 'date' in doc_data:
                    doc_data['date'] = doc_data['date'].date().isoformat()
                data.append(doc_data)
            # print(data)
            if data:
                filtered_data = [item for item in data if item.get("user_id") == user_id]
                print(filtered_data)
                transformed_data = {}
                for item in filtered_data:
                    date = item.get("date")
                    if date:
                        value = {
                                "date": date,  # Assign the correct date value
                                "pantryName": item.get("pantryName")
                            }
                        transformed_data.setdefault(date, []).append(value)

                response = {
                    "status": "1",
                    "message": "Data retrieved successfully",
                    "data": transformed_data
                }
                
            else:
                # If no data is present, return a response with a message
                response = {
                    "status": "0",
                    "message": "No data available",
                    "data": []
                }
            print(response["data"])
            return response, 200

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500


class AddPantryResource(Resource):

    def post(self, user_id):
        try:
            db = firestore.client()

            data = request.get_json()

            pantryName = data.get('pantryName')
            collection_ref = db.collection('pantry')
            document_id = collection_ref.document().id

            pantry= {
                'date': datetime.now(),
                'pantryName': pantryName,
                'user_id': user_id,
            }

            collection_ref.document(document_id).set(pantry)

            return {"success": f"Document {document_id} added to collection 'Pantry'", "document_id": document_id}

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500

class EditPantryResource(Resource):

    def put(self, doc_id):
        try:
             # Receive the updated pantry data from the request
            updated_data = request.json

            # Validate the data if necessary
            
            # Initialize Firestore client
            db = firestore.Client()
            
            # Get reference to 'pantry' collection
            doc_ref = db.collection('pantry').document(doc_id)
            
            # Update the pantry data for the given user_id

            doc_ref.update(updated_data)

             # Return a success response
            response = {
                "status": "success",
                "message": "Document data updated successfully"
            }
            return response, 200
            
            return response, 200  # 200 OK status code

        except Exception as e:
            # Handle exceptions
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500