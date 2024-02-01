# app/core/firebase.py
from firebase_admin import credentials, initialize_app,firestore

def initialize_firebase_app():
    # Replace 'firebase_credentials.json' with the actual path to your Firebase service account credentials JSON file
    cred = credentials.Certificate('firebase_credentials.json')
    firebase_app = initialize_app(cred)
    return firebase_app
