# update to route in run.py
from flask import Flask, jsonify, make_response
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.exceptions import NotFound


# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase Admin
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)

# Get Firestore database
db = firestore.client()


#create endpoint to get ingredients from firestore
@app.route('/get-ingredients', methods=['GET'])
def get_ingredients():
    try:
        #Firestore Data Fetching data of all ingredients
        collection_ref = db.collection('ingredient')
        docs = collection_ref.stream()

        data = []
        for doc in docs:
            doc_dict = doc.to_dict()
            # Construct a dictionary to handle optional fields
            ingredient = {
                "date": doc_dict.get("date", "Not specified"),  # Provide default values 
                "user_id": doc_dict.get("user_id", "Not specified"),
                "ingredient_id": doc_dict.get("ingredient_id"),
                "ingredient_name": doc_dict.get("ingredient_name"),
                "ingredient_type_code": doc_dict.get("ingredient_type_code"),
            }
            data.append(ingredient)


    except NotFound:
        return make_response(jsonify({"error": "Document not found"}), 404)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

    # Note: The status code is already included in the jsonify response
    return jsonify({
        "statusCode": 200,
        "body": data
    }), 200


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': 'Internal server error'}), 500)

if __name__ == '__main__':
    app.run(debug=True)
