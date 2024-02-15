# run.py
import secrets
from flask import Flask
from flask_restful import Api
from app.core.firebase import initialize_firebase_app
from app.api.v1.routes.resources.alpha_resource import AlphaResource
from app.api.v1.routes.resources.ingredient_resource import IngredientResource ,IngredientResourceWithCategory
from app.api.v1.routes.resources.favorite_resource import AddFavoriteResource, FavoriteResourceByUser
from app.api.v1.routes.resources.recipe_resource import GenerateRecipeFromIngredients
from app.api.v1.routes.resources.link_recipe_resource import LinkRecipeResource
from app.api.v1.routes.resources.pantry_resource import PantryResourceByUser, AddPantryResource, EditPantryResource, DeletePantryResource
from app.api.v1.routes.resources.users import Login_with_email_and_password, Logout, Sign_up_with_email_and_password, Update_Name
# import awsgi

app = Flask(__name__)
api = Api(app)
secret_key = secrets.token_hex(32)
app.secret_key = secret_key

# Use initialize_firebase_app()
initialize_firebase_app()

api.add_resource(AlphaResource, '/api/v1/alpha/<string:type>')
api.add_resource(IngredientResource, '/api/v1/ingredient/<string:user_id>')
api.add_resource(IngredientResourceWithCategory, '/api/v1/ingredient/<string:category>')
api.add_resource(AddFavoriteResource, '/api/v1/favorite')
api.add_resource(FavoriteResourceByUser, '/api/v1/favorite/<string:localId>/<string:is_favorite>')
api.add_resource(GenerateRecipeFromIngredients, '/api/v1/GenerateRecipe')
api.add_resource(LinkRecipeResource, '/api/v1/LinkRecipe')
api.add_resource(PantryResourceByUser, '/api/v1/pantry/<string:user_id>')
api.add_resource(AddPantryResource, '/api/v1/pantry/add/<string:user_id>')
api.add_resource(EditPantryResource, '/api/v1/pantry/edit/<string:doc_id>')
api.add_resource(DeletePantryResource, '/api/v1/pantry/delete/<string:pantry_id>')
api.add_resource(Login_with_email_and_password, '/login_with_email_and_password')
api.add_resource(Logout, '/logout')
api.add_resource(Sign_up_with_email_and_password, '/sign_up_with_email_and_password')
api.add_resource(Update_Name, '/update_email/<string:localId>')

# AWS Lambda handler
def lambda_handler(event, context):
    return awsgi.response(app, event, context)  # Use awsgi to wrap Flask app

# Run the application locally if not running on AWS Lambda
if __name__ == '__main__':
    app.run(debug=True)
