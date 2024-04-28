from flask import request
from flask_restful import Resource
import requests
import logging
from dotenv import load_dotenv
import os
import re
import random
from datetime import datetime

# ไม่ใช้แล้ว
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


def is_image(filename):
    # Split the filename into base name and extension
    _, ext = os.path.splitext(filename)
    # Check if the extension matches jpg, jpeg, png, or gif
    return ext.lower() in ('.jpg', '.jpeg', '.png', '.gif')

# เพิ่ม token ลงใน blacklist พร้อมระบุผู้ใช้
def getRecipeWithGoogle(data,ingredients):
    # Load environment variables from .env file
    load_dotenv()

    # Access the API key from the environment variable
    api_key = os.getenv("API_KEY_SEARCH")

    # Check if API key is available
    if not api_key:
        raise Exception("API key not found in the environment variables.")

    # Construct the URL using the API key
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=e21c2f9ab0e304589&q={ingredients}+menu&start=11"
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    # Check the status code
    status_code = response.status_code
    if status_code == 200:
        # Parse JSON response
        response_json = response.json()
        # Check if the 'items' field exists in the response
        if 'items' in response_json:
            recipe_data = []
            for item in response_json['items']:
                # Access and print relevant information
                title = item.get('title', '')

                # Access the 'pagemap' dictionary within the item
                pagemap = item.get('pagemap', {})

                # Access the 'thumbnail' list within the pagemap
                cse_image = pagemap.get('cse_image', [])

                # Iterate through each thumbnail in the list
                for thumbnail in cse_image:

                    # Access the 'src' value within the thumbnail
                    img = thumbnail.get('src', '')
                    if img.startswith('https://') and img and is_image(img):

                        # Generate a random 6-digit ID
                        random_id = ''.join(random.choices('0123456789', k=6))

                        # Get the current date and time
                        current_date = datetime.now()

                        # Format the current date as a string
                        formatted_date = current_date.strftime("%Y%m%d%H%M%S")

                        # Concatenate the current date with the random ID
                        concatenated_id = formatted_date + random_id

                        # for item1 in data:
                            # title1 = item1.get('title', '')
                            # if title != title1:
                        count_items = len(data)
                        if count_items < 10 :
                            recipe_dict = {
                                'id' : concatenated_id,
                                'title' : title,
                                'image' : img,
                            }
                            data.append(recipe_dict)
    return data




def search_menu_items(api_key, ingredients, start_index):
    # Regular expression to detect Thai characters (Thai Unicode range: U+0E00 to U+0E7F)
    # Check if ingredients contain any Thai characters
    # Combine ingredients into a single string for regex processing
    ingredients_string = ','.join(ingredients)
    print("start_index",start_index)
    
    end_index = start_index + 10

    thai_pattern =  re.compile(r'[\u0E00-\u0E7F]+')

    if thai_pattern.search(ingredients_string):
        # If Thai characters are found, use the Thai term 'สูตร' in the query ขอวิธีทำ และสูตร ไม่เอารีวิว
        url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=e21c2f9ab0e304589&q={ingredients}+วิธีทำ+สูตร+สูตรอาหาร-รีวิว&start={start_index}&end={end_index}"
        print("url",url)
    else:
        # If no Thai characters are found, proceed with the English term 'recipe'
        url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=e21c2f9ab0e304589&q={ingredients}+recipe&start={start_index}&end={end_index}"


    response = requests.get(url)
    # print("ur",url)
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    # print("data",data)
    return data.get('items', [])

def retrieve_menu_items(api_key,ingredients, total_results):
    menu_items = []
    start_index = 1
    
    total = 0
    
    while len(menu_items) < total_results:
        print("menu_items",len(menu_items))
        total += 1
        items = search_menu_items(api_key, ingredients, total)
        
        
        if not items:
            break
        
        for item in items:
            # print("total",total)
           
            # title_ = item.get('title','').split('|')

            item_title =  item.get('title','')
            

            title_parts = item_title.split('|')  # แยกด้วย |
            title_parts = title_parts[0].split('-') # แยกแต่ละส่วนด้วย - และระบุเพียงส่วนแรกเท่านั้น
            title_parts = title_parts[0].split(':')  # แยกแต่ละส่วนด้วย : และระบุเพียงส่วนแรกเท่านั้น
            title_parts = title_parts[0].split('\u2022') # แยกแต่ละส่วนด้วย • และระบุเพียงส่วนแรกเท่านั้น
            title = title_parts[0]
            
            
            # สร้างอาร์เรย์สำหรับเก็บคำที่ต้องการตรวจสอบ
            keywords_to_check = ["สล็อต","ลองเล่น","คาสิโนบาคา","รีวิวเกมสล็อต","fifa","m358e.com","พนัน"]
            if not all(keyword not in title for keyword in keywords_to_check):
                start_index += 1 
                continue
        
            
            flag_chk = False
            for item_chk in menu_items:
              
                item_title_chk =  item_chk.get('title','')
                if item_title_chk == title:
                    flag_chk = True
                    
            if not flag_chk:
                # Access the 'pagemap' dictionary within the item
                pagemap = item.get('pagemap', {})

                # Access the 'thumbnail' list within the pagemap
                cse_image = pagemap.get('cse_image', [])

                # Iterate through each thumbnail in the list
                for thumbnail in cse_image:

                    # Access the 'src' value within the thumbnail
                    img = thumbnail.get('src', '')
                    if img.startswith('https://') and img and is_image(img):
                        
                        concatenated_id = datetime.now().strftime("%Y%m%d%H%M%S") + ''.join(random.choices('0123456789', k=6))

                        recipe_dict = {
                            'id' : concatenated_id,
                            'title' : title,
                            'img' : img,
                        }

                        menu_items.append(recipe_dict)
                        start_index += len(items)   
    return menu_items[:total_results]  # Return up to the specified total_results

# ไม่ใช้แล้ว เปลี่ยนไปใช้ api with edamam แทน 28-04-2024
class GenerateRecipeFromIngredientsWithGoogle(Resource):
    def post(self):
        try:

            data = request.get_json()
            ingredients = []

            # Directly append values to the list
            for value in data.values():
                # Your logic for each ingredient goes here
                ingredients.append(value)

            # print(ingredients)
            # Load environment variables from .env file
            load_dotenv()



            # Access the API key from the environment variable
            api_key = os.getenv("API_KEY_SEARCH")

            # Check if API key is available
            if not api_key:
                raise Exception("API key not found in the environment variables.")

            menu_items = retrieve_menu_items(api_key, ingredients,10)
            return {"success": True, "recipes": menu_items}

        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            logging.error(error_message)
            return {"error": error_message}, 500
        

# current api generate recipe 28-04-2024
class GenerateRecipeFromIngredientsWithEdamam(Resource):
    def post(self):
        try:

            data = request.get_json()
            ingredients = []

           # Initialize an empty string to hold concatenated ingredients
            ingredient_string = ""

            # Loop through each value in the data dictionary
            for value in data.values():
                # Concatenate the value with a space
                ingredient_string += value + "%2"

            # Remove the trailing space
            ingredient_string = ingredient_string.strip()

            # Print or use the concatenated string
            print(ingredient_string)


            load_dotenv()
            
            # Access the API key from the environment variable
            api_key = os.getenv("API_KEY_EDAMAM")
            app_id = os.getenv("APP_ID_EDAMAM")
            print("app_id"+app_id)
            print("api_key"+api_key)
            # Check if API key is available
            if not api_key:
                raise Exception("API key not found in the environment variables.")
            
            # Check if API key is available
            if not app_id:
                raise Exception("APP ID not found in the environment variables.")
            
            url = f"https://api.edamam.com/api/recipes/v2?type=public&q={ingredient_string}&app_id={app_id}&app_key={api_key}"
            print("url"+url)

            payload = {}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)

            # print(response.text)
            response_json = response.json()
            print(response_json)
             
            # hits = data.get('hits', [])
            # print("data "+data)
            
            recipe_data = []
            if 'hits' in response_json and response_json.get('hits') != []:
              
                for item in response_json['hits']:
                    recipe =  item.get('recipe','')
                    label = recipe.get('label','')
                    image = recipe.get('image','')
                    concatenated_id = datetime.now().strftime("%Y%m%d%H%M%S") + ''.join(random.choices('0123456789', k=6))
                     
                    recipe_dict = {
                            'id' : concatenated_id,
                            'title' : label,
                            'img' : image,
                    }

                    recipe_data.append(recipe_dict)
                        
                        
                    print("label :"+label)
                    # print("<br>")
            
                return recipe_data
            else:
                return {"error": 'not found!'}, 404
            
        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            logging.error(error_message)
            return {"error": error_message}, 500

