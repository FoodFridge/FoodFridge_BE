from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore
# import logging
class FavoriteResourceByUser(Resource):
    def get(self,user_id,is_favorite):
        try:
            
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
        
            db = firestore.client()
            collection_ref = db.collection('favorite')
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
                transformed_data = {}
                for item in data:
                    recipe_name = item.get("data", {}).get("recipe_name")
                    if recipe_name:
                    # Exclude 'recipeName' from the value part
                        value = {
                             "favId": item.get("document_id"),
                             "img": item.get("data", {}).get("img"),
                             "title": item.get("data", {}).get("title"),
                             "url": item.get("data", {}).get("url"),
                             "isFavorite": item.get("data", {}).get("status"),
                             "userId": item.get("data", {}).get("user_id")
                         }
                        transformed_data.setdefault(recipe_name,[]).append(value)
                # Creating the final response structure
                response_data = [{"recipeName": key, "recipeLinks": value} for key, value in transformed_data.items()]

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
            response = {
                    "status": "1",
                    "message": "Data updated successfully",
            }
            return response, 200
        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500

