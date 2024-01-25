from flask import Flask, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

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
            data.append(doc.to_dict())


    except NotFound:
        return make_response(jsonify({"error": "Document not found"}), 404)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

    return jsonify(data)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': 'Internal server error'}), 500)

if __name__ == '__main__':
    app.run(debug=True)
