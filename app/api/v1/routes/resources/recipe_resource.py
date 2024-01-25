from flask import request
from flask_restful import Resource
import requests
from app.core.firebase import initialize_firebase_app, firestore
import logging
from dotenv import load_dotenv
import os

class GenerateRecipeFromIngredients(Resource):

    def get(self):   

        try:
            #อาจจะต้องดูตอนรับ Param ว่าเป็นแบบไหน
            ingredients_tuple = request.form.getlist('ingredients')
            
            if ingredients_tuple:
                ingredients = ingredients_tuple[0]
                # Your implementation here
                # print('ingredients',ingredients)

                querystring = {
                "ingredients": ingredients,
                "number":"5",
                "ignorePantry":"true",
                "ranking":"1"
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
                } #hide key?
                response = requests.get(url, headers=headers, params=querystring)

                if response.status_code == 200:
                # Parse and work with the API response (in JSON format, for example)
                    api_data = response.json()
                    logging.info(api_data)
                    return {"success": True, "recipes": api_data}
                else:
                # Handle the error
                    error_message = f"Error: {response.status_code} - {response.text}"
                    logging.error(error_message)
                return {"error": f"Error: {response.status_code} - {response.text}"}, 500

                # print(response.json())
                # return {"success": True, "ingredients": ingredients}
            else:
                return {"error": "No ingredients found in the request"}, 400

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            logging.error(error_message)
            return {"error": error_message}, 500
