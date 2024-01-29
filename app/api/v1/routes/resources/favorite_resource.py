from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore
# import logging

class FavoriteResourceByUser(Resource):
    def get(self, user_id,is_favorite):
        try:

            db = firestore.client()

            collection_ref = db.collection('favorite')
            # docs = collection_ref.stream()

            # Construct the query
            query = collection_ref.where('status', '==', is_favorite).where('user_id', '==', user_id)
            docs = query.stream()

            data = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_id = doc.id  # Get the document_id
    
                # Append the document_id along with the data to the 'data' list
                data.append({"document_id": doc_id, "data": doc_data})

            response = {}
            if data:
                # If data is present, return a success response
                print('data', data)
                # Filter data based on the condition (alph_val equals "Carb")
                filtered_data = [
                    {"favId": item.get("document_id"), "img": item["data"].get("img"), "title": item["data"].get("title"), "recipeName": item["data"].get("recipe_name"),
                     "url": item["data"].get("url"),"isFavorite": item["data"].get("status")}
                    for item in data 
                    
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


class AddFavoriteResource(Resource):
    #to do find user id
    def post(self):
        try:
            # parameter json
            data = request.get_json()

            favId = data.get('favId')
            isFavorite = data.get('isFavorite')
            
            # Create a Firestore client
            db = firestore.client()

            # Specify the collection reference
            collection_ref = db.collection('favorite')

            # Reference to the specific document
            document_ref = collection_ref.document(favId)

            # Update the 'status' field to a new value (e.g., 'Y' for 'Yes')
            document_ref.update({'status': isFavorite})

            return {"success": f"Document {favId} added to collection 'Favorite'", "document_id": favId}

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500
