from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore


class RecipeResource(Resource):


    def put(self):
        try:
            db = firestore.client()

            recipe_txn_name = request.form.get('recipe_txn_name')
            created_date = request.form.get('created_date')
            created_by = request.form.get('created_by')
            rating = request.form.get('rating')
            cooking_time = request.form.get('cooking_time')
            
            collection_ref = db.collection('recipe_txn')
            document_id = collection_ref.document().id

            print(request.form.get('recipe_txn_name'))
            data = {
                'recipe_txn_name': recipe_txn_name,
                'created_date': created_date,
                'created_by': created_by,
                'rating': rating,
                'cooking_time': cooking_time,
                # Add more fields as needed
            }

            

            
            collection_ref.document(document_id).set(data)

            return {"success": f"Document {document_id} added to collection 'recipe_txn'"}

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500

