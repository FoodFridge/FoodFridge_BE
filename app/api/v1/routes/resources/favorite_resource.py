from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore
# import logging


class FavoriteResourceByUser(Resource):
    def get(self, user_id):
        try:
            # # Use initialize_firebase_app() in your code
            # initialize_firebase_app()

            db = firestore.client()

            collection_ref = db.collection('favorite')
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
                    {"fav_id": item.get("fav_id"), "img": item.get("img"), "title": item.get("title"), "recipeName": item.get("recipeName"), 
                     "url": item.get("url")}
                    for item in data if item.get("user_id") == user_id and item.get("status") == "Y"
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
            db = firestore.client()

            data = request.get_json()

            img = data.get('img')
            status = data.get('status')
            recipeName = data.get('recipeName')
            title = data.get('title')
            url = data.get('url')
            user_id = data.get('user_id')
            print(recipeName)
            collection_ref = db.collection('favorite')
            document_id = collection_ref.document().id

          
            favorite= {
                "status" : status,
                'img': img,
                'recipeName': recipeName,
                'title': title,
                'url': url,
                'user_id': user_id,
                # Add more fields as needed
            }

            
            collection_ref.document(document_id).set(favorite)

            return {"success": f"Document {document_id} added to collection 'Favorite'", "document_id": document_id}

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500
