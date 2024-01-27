# run.py
from flask import Flask
from flask_restful import Api
from app.core.firebase import initialize_firebase_app, firestore
from app.api.v1.routes.resources.alpha_resource import AlphaResource
from app.api.v1.routes.resources.ingredient_resource import IngredientResource ,IngredientResourceWithCategory
from app.api.v1.routes.resources.favorite_resource import AddFavoriteResource, FavoriteResourceByUser, FavoriteResourceByFavID, ChangeFavoriteResource
from app.api.v1.routes.resources.recipe_resource import GenerateRecipeFromIngredients
from app.api.v1.routes.resources.google_resource import SearchWithRecipe
from app.api.v1.routes.resources.pantry_resource import PantryResourceByUser, AddPantryResource

app = Flask(__name__)
api = Api(app)  # Initialize the Api object

 # Use initialize_firebase_app() in your code
initialize_firebase_app()

# Add the API resource to the app
api.add_resource(AlphaResource, '/api/v1/aplha/<string:type>')
api.add_resource(IngredientResource, '/api/v1/ingredient/')
api.add_resource(IngredientResourceWithCategory, '/api/v1/ingredient/<string:category>')
api.add_resource(AddFavoriteResource, '/api/v1/favorite/add/<string:user_id>')
api.add_resource(FavoriteResourceByUser, '/api/v1/favorite/<string:user_id>')
api.add_resource(FavoriteResourceByFavID, '/api/v1/favorite/<string:user_id>/<string:fav_id>')
api.add_resource(ChangeFavoriteResource, '/api/v1/favorite/change')
api.add_resource(GenerateRecipeFromIngredients, '/api/v1/GenerateRecipe/')
api.add_resource(SearchWithRecipe, '/api/v1/search/<string:recipeName>')
api.add_resource(AddPantryResource, '/api/v1/pantry/add/<string:user_id>')
api.add_resource(PantryResourceByUser, '/api/v1/pantry/<string:user_id>')


if __name__ == '__main__':
    app.run(debug=True)

