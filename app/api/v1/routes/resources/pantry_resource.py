import json
from flask import Flask, request, jsonify
from flask_restful import Resource
from app.core.firebase import initialize_firebase_app, firestore
from datetime import datetime
import logging
# from google.cloud.firestore_v1 import DatetimeWithNanoseconds

app = Flask(__name__)


class PantryResourceByUser(Resource):
    def get(self, user_id):
        try:
            db = firestore.client()
            collection_ref = db.collection('pantry')
            docs = collection_ref.where("user_id", "==", user_id).stream()
            # print(docs)
            data = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['doc_id'] = doc.id
                if 'date' in doc_data:
                    doc_data['date'] = doc_data['date'].date().isoformat()
                data.append(doc_data)
            print(data)
            if data:

                transformed_data = {}
                for item in data:
                    date = item.get("date")
                    if date:
                        value = {
                                "pantryName": item.get("pantryName"),
                                "doc_id": item.get("doc_id"),
                            }
                        transformed_data.setdefault(date, []).append(value)

                response_data = [{"date": key, "pantryInfo": value} for key, value in transformed_data.items()]


                sorted_response_data = sorted(response_data, key=lambda x: x['date'])

                response = {
                    "status": "1",
                    "message": "Data retrieved successfully",
                    "data": sorted_response_data
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

        except Exception as e:
            # Handle exceptions
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500
        
        
class DeletePantryResource(Resource):
    def delete(self, doc_id):
        try:
            # Initialize Firestore client
            db = firestore.client()

            # Query the 'pantry' collection to find documents with matching user_id
            doc_ref = db.collection('pantry').document(doc_id)
            

            # Delete each document found with the matching user_id
            doc_ref.delete()

            # Return a success response
            response = {
                "status": "success",
                "message": f"All pantry document of pantry {doc_id} deleted successfully"
            }
            return response, 200

        except Exception as e:
            # Handle exceptions
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500
