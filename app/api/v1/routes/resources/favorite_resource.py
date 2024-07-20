from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore
from app.api.v1.routes.resources.auth_resource import authorization, messageWithStatusCode
# import logging

# class FavoriteRecipeResourceByUser(Resource):
#     #to do find user id
#     def post(self):
#         try:
#             # parameter json
#             data = request.get_json()
#             favId = data.get('favId')
#             isFavorite = data.get('isFavorite')
#             # Create a Firestore client
#             db = firestore.client()
#             # Specify the collection reference
#             collection_ref = db.collection('recipes')
#             # Reference to the specific document
#             document_ref = collection_ref.document(favId)
#             # Update the 'status' field to a new value (e.g., 'Y' for 'Yes')
#             document_ref.update({'favorite_status': isFavorite})
#             response = {
#                     "status": "1",
#                     "message": "Data updated successfully",
#             }
#             return response, 200
#         except Exception as e:
#             # Handle the exception and return an appropriate response
#             error_message = f"An error occurred: {str(e)}"
#             return {"error": error_message}, 500
        
        
# class FavoriteResourceByUser(Resource):
#     def get(self,localId,is_favorite):
#         try:


#             # Check if 'Authorization' header exists
#             # authorization_header = request.headers.get('Authorization')
#             # if authorization_header and authorization_header.startswith('Bearer '):
#             #     id_token = authorization_header.split(' ')[1]
#             # else:
#             #     # Return error response if 'Authorization' header is missing or invalid
#             #     return {"error": "Missing or invalid Authorization header"}, 401

#             # # Verify the ID token before proceeding
#             # decoded_token = auth.verify_id_token(id_token)

#             # if not decoded_token['uid']:
#             #     return {"error": "uid invalid."}, 401
#             # user_timezone = request.headers.get('User-Timezone')

#             code, response = authorization(localId)
#             if code != 200:
#                 return response, code
        
#             db = firestore.client()
#             collection_ref = db.collection('favorite')
#             query = collection_ref.where('status', '==', is_favorite).where('user_id', '==', localId)
#             docs = query.stream()
#             data = []
#             for doc in docs:
#                 doc_data = doc.to_dict()
#                 doc_id = doc.id  # Get the document_id
#                 # Append the document_id along with the data to the 'data' list
#                 data.append({"document_id": doc_id, "data": doc_data})
            
#             response = {}
#             if data:
#                 transformed_data = {}
#                 for item in data:
#                     recipe_name = item.get("data", {}).get("recipe_name")
#                     if recipe_name:
#                     # Exclude 'recipeName' from the value part
#                         value = {
#                              "favId": item.get("document_id"),
#                              "img": item.get("data", {}).get("img"),
#                              "title": item.get("data", {}).get("title"),
#                              "url": item.get("data", {}).get("url"),
#                              "isFavorite": item.get("data", {}).get("status"),
#                              "userId": item.get("data", {}).get("user_id")
#                          }
#                         transformed_data.setdefault(recipe_name,[]).append(value)
#                 # Creating the final response structure
#                 response_data = [{"recipeName": key, "recipeLinks": value} for key, value in transformed_data.items()]

#                 response = {
#                     "status": "1",
#                     "message": "Data retrieved successfully",
#                     "data": response_data
#                 }
#             else:
#                 # If no data is present, return a response with a message
#                 response = {
#                     "status": "0",
#                     "message": "No data available",
#                     "data": []
#                 }
#             return response, 200
#         except Exception as e:
#             # Handle the exception and return an appropriate response
#             error_message = f"An error occurred: {str(e)}"
#             return {"error": error_message}, 500
        
# class AddFavoriteResource(Resource):
#     #to do find user id
#     def post(self):
#         try:
#             # parameter json
#             data = request.get_json()
#             favId = data.get('favId')
#             isFavorite = data.get('isFavorite')
#             # Create a Firestore client
#             db = firestore.client()
#             # Specify the collection reference
#             collection_ref = db.collection('favorite')
#             # Reference to the specific document
#             document_ref = collection_ref.document(favId)
#             # Update the 'status' field to a new value (e.g., 'Y' for 'Yes')
#             document_ref.update({'status': isFavorite})
#             response = {
#                     "status": "1",
#                     "message": "Data updated successfully",
#             }
#             return response, 200
#         except Exception as e:
#             # Handle the exception and return an appropriate response
#             error_message = f"An error occurred: {str(e)}"
#             return {"error": error_message}, 500


class FavoriteRecipeByLocalIDResource(Resource):
    #to do find user id
    def get(self,local_id):
        try:
            print("local_id",local_id)
            db = firestore.client()
            collection_ref = db.collection('recipes')
            query = collection_ref.where('favorite_status', '==', 'Y').where('local_id', '==', local_id)
            docs = query.stream()
        
            doc_data = []  # ตั้งค่าเริ่มต้นเป็นลิสต์เปล่า

            for doc in docs:
                doc_data.append(doc.to_dict())  # เพิ่มข้อมูลแต่ละ doc ในลิสต์
        
            recipe_data = []
            if doc_data:
                for item in doc_data:
        
                    recipe_dict = {
                        'id' :  item.get('id'),
                        'title' :  item.get('title'),
                        'img' :  item.get('img'),
                        'link' :  item.get('link'),
                        'favorite_status' :  item.get('favorite_status'),
                        'local_id' : local_id
                    }
                                            
                    recipe_data.append(recipe_dict)
                return recipe_data
            else:
                return {"error": 'not found!'}, 404

                                 
        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500



class FavoriteRecipeResource(Resource):
    #to do find user id
    def post(self):
        try:
            # parameter json
            data = request.get_json()
            favId = data.get('favId')
            isFavorite = data.get('isFavorite')
            
            
            # Create a Firestore client
            
            db = firestore.client()

            # Specify the collection and document reference
            collection_ref = db.collection('recipes')
            document_ref = collection_ref.document(favId)

            # Check if the document exists
            doc = document_ref.get()
            if doc.exists:

                local_id = doc.to_dict().get('local_id')
                print(f"Current local_id: {local_id}")

                # Update the 'status' field to the new value
                document_ref.update({'favorite_status': isFavorite})

                # query = collection_ref.where('local_id', '==', local_id)
                # docs = query.stream()
                # dataResult = []

                # for doc in docs:
                #     dataResult.append(doc.to_dict())


                # recipe_data = []
                # # กรณี - มีข้อมูล recipe
                # if dataResult:
                #     for item in dataResult:             
                       
                #         recipe_dict = {
                #             'id' : item.get('id'),
                #             'title' : item.get('title'),
                #             'img' : item.get('img'),
                #             'link' : item.get('link'),
                #             'favorite_status' : item.get('favorite_status'),
                #             'local_id' : local_id
                #         }
                                            
                #         recipe_data.append(recipe_dict)

                # return recipe_data, 200

                db = firestore.client()
                collection_ref = db.collection('recipes')
                query = collection_ref.where('favorite_status', '==', 'Y').where('local_id', '==', local_id)
                docs = query.stream()
            
                doc_data = []  # ตั้งค่าเริ่มต้นเป็นลิสต์เปล่า

                for doc in docs:
                    doc_data.append(doc.to_dict())  # เพิ่มข้อมูลแต่ละ doc ในลิสต์
            
                recipe_data = []
                if doc_data:
                    for item in doc_data:
            
                        recipe_dict = {
                            'id' :  item.get('id'),
                            'title' :  item.get('title'),
                            'img' :  item.get('img'),
                            'link' :  item.get('link'),
                            'favorite_status' :  item.get('favorite_status'),
                            'local_id' : local_id
                        }
                                                
                        recipe_data.append(recipe_dict)
                    return recipe_data
                else:
                    return {"error": 'not found!'}, 404
            else:
                return {"error": "No data found"}, 404
            

            
          
            
        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500

