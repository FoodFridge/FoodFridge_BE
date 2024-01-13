# run.py
from flask import Flask
from flask_restful import Api
from app.core.firebase import initialize_firebase_app, firestore
from app.api.v1.routes.resources.alpha_resource import AlphaResource
from app.api.v1.routes.resources.ingredient_resource import IngredientResource ,IngredientResourceWithCategory

app = Flask(__name__)
api = Api(app)  # Initialize the Api object

 # Use initialize_firebase_app() in your code
initialize_firebase_app()

# Add the API resource to the app
api.add_resource(AlphaResource, '/api/v1/aplha/<string:type>')
api.add_resource(IngredientResource, '/api/v1/ingredient/')
api.add_resource(IngredientResourceWithCategory, '/api/v1/ingredient/<string:category>')

if __name__ == '__main__':
    app.run(debug=True)

