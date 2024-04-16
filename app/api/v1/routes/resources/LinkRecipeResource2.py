from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import auth, initialize_app, credentials
from app.core.firebase import initialize_firebase_app, firestore
from app.api.v1.routes.resources.auth_resource import authorization, messageWithStatusCode 
from app.api.v1.routes.resources.recipe_resource import is_image
import requests
from dotenv import load_dotenv
import os
import uuid
import traceback
import re
import random
from datetime import datetime

def search_menu_items_recipe(api_key, recipe_name, start_index):
    
    end_index = start_index + 10

    # If no Thai characters are found, proceed with the English term 'recipe'
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=e21c2f9ab0e304589&q={recipe_name}+recipe&start={start_index}&end={end_index}"

    response = requests.get(url)
    # print("ur",url)
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    # print("data",data)
    return data.get('items', [])

def retrieve_menu_items_recipe(api_key,ingredients, total_results):
    menu_items = []
    start_index = 1
    
    total = 0
    
    while len(menu_items) < total_results:
        print("menu_items",len(menu_items))
        total += 1
        items = search_menu_items_recipe(api_key, ingredients, total)
        
        
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
            keywords_to_check = ["สล็อต","ลองเล่น","คาสิโนบาคา","รีวิวเกมสล็อต","fifa","m358e.com","พนัน","รีวิว"]
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

class LinkRecipeResource2(Resource):
    def post(self):
        try:
            # parameter json
            data = request.get_json()

            localId = data.get('localId')
            recipe_name = data.get('recipeName')

            # Load environment variables from .env file
            load_dotenv()

            # Access the API key from the environment variable
            api_key = os.getenv("API_KEY_SEARCH")

            # Check if API key is available
            if not api_key:
                raise Exception("API key not found in the environment variables.")

            # Construct the URL using the API key
            url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=e21c2f9ab0e304589&q={recipe_name}"
            payload = {}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)

            # Check the status code
            status_code = response.status_code

            # Check if the request was successful (status code 200)
            if response.status_code == 200:

                # Parse JSON response
                response_json = response.json()

                # Create a batch object
                db = firestore.client()
                batch = db.batch()
                links = []

                 # Check if the 'items' field exists in the response
                if 'items' in response_json:

                    for item in response_json['items']:
                        # Access and print relevant information
                        title = item.get('title', '')
                        link = item.get('link', '')

                        # กรณีไม่มี localId
                        if not localId:
                            if link.startswith('https://'):
                                # Access the 'pagemap' dictionary within the item
                                pagemap = item.get('pagemap', {})

                                # Access the 'thumbnail' list within the pagemap
                                cse_image = pagemap.get('cse_image', [])

                                # Initialize img variable
                                img = ''

                                # Iterate through each thumbnail in the list
                                for thumbnail in cse_image:
                                    # Access the 'src' value within the thumbnail
                                    img = thumbnail.get('src', '')
                                    if img.startswith('https://') and img and is_image(img):

                                        favorite = {
                                            "favId": str(uuid.uuid4()),
                                            'img': img,
                                            "title": recipe_name,
                                            'url': link,
                                            'title': title,
                                            "isFavorite": 'None',
                                            "userId": 'None'
                                            # Add more fields as needed
                                        }
                                    links.append(favorite)

                        else:
                            user_timezone = request.headers.get('User-Timezone')

                            code = authorization(localId,user_timezone)
                            print("code",code)
                            if code != "":
                                message = messageWithStatusCode(code)
                                return {'message': message},code

                            collection_ref = db.collection('favorite')
                            # docs = collection_ref.stream()

                            # Construct the query
                            query = collection_ref.where('recipe_name', '==', recipe_name).where('user_id', '==', localId)
                            docs = query.stream()

                            dataFav = []
                            for doc in docs:
                                doc_data = doc.to_dict()

                                dataFav.append(doc_data)

                            # Check if the title is not present in dataFav
                            if all(doc.get('title', '') != title for doc in dataFav):
                                link = item.get('link', '')
                                print(link)

                                # Check if the link is an HTTP link before inserting
                                if link.startswith('https://'):
                                    # Access the 'pagemap' dictionary within the item
                                    pagemap = item.get('pagemap', {})

                                    # Access the 'thumbnail' list within the pagemap
                                    cse_image = pagemap.get('cse_image', [])

                                    # Initialize img variable
                                    img = ''

                                    # Iterate through each thumbnail in the list
                                    for thumbnail in cse_image:
                                        # Access the 'src' value within the thumbnail
                                        img = thumbnail.get('src', '')
                                        if img.startswith('https://') and img and is_image(img):

                                            favorite = {
                                                "status": 'N',
                                                'img': img,
                                                'recipe_name': recipe_name,
                                                'title': title,
                                                'url': link,
                                                'user_id': localId,
                                                # Add more fields as needed
                                            }

                                            # Reference to the 'favorite' collection
                                            collection_ref = db.collection('favorite')

                                            # Create a new document reference in the batch
                                            document_ref = collection_ref.document()

                                            # Set data for the document in the batch
                                            batch.set(document_ref, favorite)

                        # Commit the batch
                        batch.commit()

                # response = {}
                if localId:

                    collection_ref = db.collection('favorite')

                    # Construct the query using filter keyword argument
                    query = collection_ref.where('recipe_name', '==', recipe_name).where('user_id', '==', localId)

                    # Alternatively, you can use filter keyword argument directly
                    # query = collection_ref.where(recipe_name='recipe_name', user_id='localId')

                    docs = query.stream()
                    dataResult = []

                    for doc in docs:
                        doc_data = doc.to_dict()
                        doc_id = doc.id  # Get the document_id
                        # Append the document_id along with the data to the 'data' list
                        dataResult.append({"document_id": doc_id, "data": doc_data})

                    if dataResult:
                        transformed_data = []
                        for item in dataResult:

                            value = {
                                "favId": item.get("document_id"),
                                "img": item["data"].get("img"),
                                "title": item["data"].get("title"),
                                "url": item["data"].get("url"),
                                "isFavorite": item["data"].get("status"),
                                "userId": item["data"].get("user_id")
                            }
                            transformed_data.append(value)

                            response = {
                                "status": "1",
                                "message": "Data retrieved successfully",
                                "data": transformed_data
                            }

                    else:
                        # If no data is present, return a response with a message
                        response = {
                            "status": "0",
                            "message": "No data available",
                            "data": []
                        }
                    return response, 200


                else:
                    if links:
                        response = {
                            "status": "1",
                            "message": "Data retrieved successfully",
                            "data": links
                        }

                    return response, 200

            else:

                print(f"Error: {status_code}")
                return status_code

        except NameError:
                traceback.print_exc(limit=1)  # Print the traceback with limit 1 to only show the line that raised the exception
                print("Variable 'my_variable' is not defined.")
        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500
