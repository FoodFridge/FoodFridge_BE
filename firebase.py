import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

#authenticate to firebase
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)

#storing client db data to firebase
db = firestore.client()
# db.collection("person").add({'name': 'Johny', 'age': '40'})
db.collection("ingredient").add({'ingredient_id': '40', 'ingredient_name': 'Grains', 'ingredient_type_code': '01' })

