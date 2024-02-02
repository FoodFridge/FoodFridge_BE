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
                    doc_data['date'] = doc_data['date'].isoformat()  # Convert to ISO format
                data.append(doc_data)

            if data:
                # If data is present, return a success response
                filtered_data = [
                    {"date": item.get("date"), "pantryName": item.get("pantryName")}
                    for item in data if item.get("user_id") == user_id
                ]
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