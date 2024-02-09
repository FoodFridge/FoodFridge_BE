import json
from flask import Flask, request, jsonify
from flask_restful import Resource
from app.core.firebase import initialize_firebase_app, firestore
from datetime import datetime
import logging
import uuid
# from google.cloud.firestore_v1 import DatetimeWithNanoseconds

app = Flask(__name__)

random_uuid = uuid.uuid4()
random_uuid_str = str(random_uuid)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

class PantryResourceByUser(Resource):
    def get(self, user_id):
        try:
            db = firestore.client()
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
                                "pantry_id": item.get("pantry_id"),
                                "pantryName": item.get("pantryName")
                            }
                        transformed_data.setdefault(date, []).append(value)

                response_data = [{"date": key, "pantryInfo": value} for key, value in transformed_data.items()]

                response = {
                    "status": "1",
                    "message": "Data retrieved successfully",
                    "data": response_data
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
                'pantry_id': random_uuid_str,
                'ingredient_type_code': '08',
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
            db = firestore.client()
            
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
        
        
class DeletePantryResource(Resource):
    def delete(self, pantry_id):
        try:
            # Initialize Firestore client
            db = firestore.client()

            # Query the 'pantry' collection to find documents with matching user_id
            query_ref = db.collection('pantry').where("pantry_id", "==", pantry_id)
            docs = query_ref.stream()

            # Delete each document found with the matching user_id
            for doc in docs:
                doc_ref = db.collection('pantry').document(doc.id)
                doc_ref.delete()

            # Return a success response
            response = {
                "status": "success",
                "message": f"All pantry documents for user with ID {pantry_id} deleted successfully"
            }
            return response, 200

        except Exception as e:
            # Handle exceptions
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500
