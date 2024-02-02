from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore
import secrets
import random
import string
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
                     "url": item["data"].get("url"),"isFavorite": item["data"].get("status"),"userId": item["data"].get("user_id")}
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

        #จำเป็นไหม? ส่ง Document Id ยังไง และ ถ้าไม่ใช้ fav id ให้กลับไปแก้
class FavoriteResourceByFavID(Resource):
    def get(self, user_id, fav_id):
        try:
            db = firestore.client()

            collection_ref = db.collection('favorite')
            docs = collection_ref.stream()

            data = []
            for doc in docs:
                data.append(doc.to_dict())

            if data:

                filtered_data = [
                    {"img": item.get("img"), "title": item.get("title"), "recipeName": item.get("recipeName"), "status": item.get("status") , 
                     "url": item.get("url")}
                    for item in data if item.get("user_id") == user_id and item.get("fav_id") == fav_id
                ]

                print(filtered_data)

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
        
class ChangeFavoriteResource(Resource):
    def put(self):
        try:
            db = firestore.client()

            data = request.get_json()

            document_id = data.get('document_id')

            if not document_id:
                return {"error": "Missing required parameters"}, 400
            
            collection_name = 'favorite'
            doc_ref = db.collection(collection_name).document(document_id)
            current_status = doc_ref.get().get('status')
            new_status = 'N' if current_status == 'Y' else 'Y'

            doc_ref.update({'status': new_status})
            return {"success": f"Favorite status toggled for document ID {document_id}. New status: {new_status}"}

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500