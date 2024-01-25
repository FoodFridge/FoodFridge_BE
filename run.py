# run.py
from flask import Flask
from flask_restful import Api
from app.core.firebase import initialize_firebase_app, firestore
from app.api.v1.routes.resources.alpha_resource import AlphaResource
from app.api.v1.routes.resources.ingredient_resource import IngredientResource ,IngredientResourceWithCategory
from app.api.v1.routes.resources.favorite_resource import AddFavoriteResource, FavoriteResourceByUser
from app.api.v1.routes.resources.google_resource import SearchWithRecipe

app = Flask(__name__)
api = Api(app)  # Initialize the Api object

 # Use initialize_firebase_app() in your code
initialize_firebase_app()

# Add the API resource to the app
api.add_resource(AlphaResource, '/api/v1/aplha/<string:type>')
api.add_resource(IngredientResource, '/api/v1/ingredient/')
api.add_resource(IngredientResourceWithCategory, '/api/v1/ingredient/<string:category>')
api.add_resource(AddFavoriteResource, '/api/v1/favorite')
api.add_resource(FavoriteResourceByUser, '/api/v1/favorite/<string:user_id>')
api.add_resource(SearchWithRecipe, '/api/v1/search/<string:recipeName>')
if __name__ == '__main__':
    app.run(debug=True)

