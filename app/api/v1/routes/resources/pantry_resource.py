from flask import jsonify, request
from flask_restful import Resource
from app.core.firebase import firestore
from datetime import datetime
import pytz,re
from app.api.v1.routes.resources.auth_resource import authorization, messageWithStatusCode
import json


class PantryResourceByUser(Resource):
    def get(self, localId):
        try:

            user_timezone = request.headers.get('User-Timezone')
            code = authorization(localId, user_timezone)
            print("code",code)
            if code != "":
                message = messageWithStatusCode(code)
                return {'message': message},code

           # Regular expression pattern to match "America" in a case-insensitive manner
            pattern = re.compile(r'(?i)America')

            # Check if the pattern is found in the string
            found = bool(re.search(pattern, user_timezone))

            db = firestore.client()
            collection_ref = db.collection('pantry')
            docs = collection_ref.stream()
            

            data = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_data['doc_id'] = doc.id
                if 'date' in doc_data:
                    
                    # ดึงข้อมูล datetime UTC จาก Firebase
                    utc_time_from_firebase = doc.to_dict()['date']

                    # กำหนดโซนเวลาของไทย
                    thai_timezone = pytz.timezone(user_timezone)
                    

                    # แปลงเวลา UTC เป็นเวลาในโซนเวลาไทย
                    local_time = utc_time_from_firebase.astimezone(thai_timezone)

                    # Format the date as 'dd/mm/yyyy'
                    if found:
                        formatted_date = local_time.strftime('%m/%d/%Y')
                    else:
                        formatted_date = local_time.strftime('%d/%m/%Y')
                    doc_data['date'] = formatted_date
                    # doc_data['date'] = doc_data['date'].date().isoformat()
                data.append(doc_data)

            if data:
                filtered_data = [item for item in data if item.get("user_id") == localId]
                print(filtered_data)
                transformed_data = {}
                for item in filtered_data:
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
            # print(response["data"])
            return response, 200

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500


class AddPantryResource(Resource):
    def post(self, localId):
        try:
            db = firestore.client()

            data = request.get_json()

            pantryName = data.get('pantryName')
            collection_ref = db.collection('pantry').where("pantryName", "==", pantryName).where("user_id", "==", localId).stream()
            

            # collection_ref = db.collection('users')
            # docs = collection_ref.where("email", "==", email).stream()
            
            if any(collection_ref):

                response = {
                    "status": "1",
                    "message": "Pantry has already!",
                }
                  
                return response, 409 

            
            collection_ref = db.collection('pantry')
            document_id = collection_ref.document().id
            pantry= {
                'date': datetime.now(),
                'pantryName': pantryName,
                'ingredient_type_code': '01',
                'user_id': localId,
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
            doc_ref.delete()

            # Return a success response
            response = {
                "status": "success",
                "message": f"All pantry documents for user with ID {doc_id} deleted successfully"
            }
            return response, 200

        except Exception as e:
            # Handle exceptions
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500


class SearchIngredientResource(Resource):
    def post(self):
        try:
            # Read data from ingredients.json file
            with open("ingredients.json", "r") as file:
                data = json.load(file)

            # print('data', data)

            # Process the data as needed
            # For example, you can filter based on the ingredient parameter

            # Assuming 'ingredient' is a parameter from the GET request
            data2 = request.get_json()
            ingredient = data2.get('ingredient')

            # Perform search logic using 'ingredient' and 'data'
            matching_results = []
            for item in data:
                if ingredient.lower() in item.lower():  # Case-insensitive search
                    
                    matching_results.append(item)
            
            # print(matching_results)

            return matching_results, 200

        except Exception as e:
            # Handle exceptions
            return {"error": str(e)}, 500  # Placeholder error response