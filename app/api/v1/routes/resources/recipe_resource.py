from flask import request
from flask_restful import Resource
import requests
import logging
from dotenv import load_dotenv
import os

class GenerateRecipeFromIngredients(Resource):
    def post(self):
        try:

            data = request.get_json()
            ingredients = []

            # Directly append values to the list
            for value in data.values():
                # Your logic for each ingredient goes here
                ingredients.append(value)

            print(ingredients)

            querystring = {
                "ingredients": ",".join(ingredients),
                "number": 10,
                "ignorePantry": "true",
                "ranking": 1
            }
            load_dotenv()

            api_key = os.getenv("RAPIDAPI_KEY")

            # Check if API key is available
            if api_key is None:
                raise ValueError("API key is not set. Make sure to set it in the .env file.")

            url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/findByIngredients"
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
            }
            response = requests.get(url, headers=headers, params=querystring)

            if response.status_code == 200:
                # Parse and work with the API response (in JSON format, for example)
                api_data = response.json()
                recipe_data = []
                for recipe in api_data:

                    recipe_dict = {
                        'id' : recipe["id"],
                        'title' : recipe["title"],
                        'image' : recipe["image"],
                    }
                    recipe_data.append(recipe_dict)

                return {"success": True, "recipes": recipe_data}
            
            else:
                # Handle the error
                error_message = f"Error: {response.status_code} - {response.text}"
                logging.error(error_message)
                return {"error": f"Error: {response.status_code} - {response.text}"}, 500

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            logging.error(error_message)
            return {"error": error_message}, 500