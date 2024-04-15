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

def search_menu_items_link(api_key, recipe_name, start_index):
    
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

def retrieve_menu_items_link(api_key,recipe_name, total_results,local_id):
    menu_items = []
    start_index = 1
    total = 0
    
    # Create a batch object
    db = firestore.client()
    batch = db.batch()
    links = []
                
    while len(menu_items) < total_results:
        total += 1
        items = search_menu_items_link(api_key, recipe_name, total)
         
        if not items:
            break
        
        for item in items:
            item_title =  item.get('title','')
            item_link = item.get('link', '')
            
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
                    
            # ถ้ามี local_id ให้เช็ค timezone & author
            if local_id:
                user_timezone = request.headers.get('User-Timezone')

                code = authorization(local_id,user_timezone)
                if code != "":
                    message = messageWithStatusCode(code)
                    return {'message': message},code

                collection_ref = db.collection('favorite')

                # Construct the query
                query = collection_ref.where('recipe_name', '==', recipe_name).where('user_id', '==', local_id)
                docs = query.stream()

                dataFav = []
                # get db favorite ของ local_id นั้นๆ
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
                                    'user_id': local_id,
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
                    
            # มี local_id - get ข้อมูลจาก database
            if not flag_chk and local_id:      
                collection_ref = db.collection('favorite')

                # Construct the query using filter keyword argument
                query = collection_ref.where('recipe_name', '==', recipe_name).where('user_id', '==', local_id)

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
                    for item in dataResult:

                        value = {
                            "favId": item.get("document_id"),
                            "img": item["data"].get("img"),
                            "title": item["data"].get("title"),
                            "url": item["data"].get("url"),
                            "isFavorite": item["data"].get("status"),
                            "userId": item["data"].get("user_id")
                        }
                        menu_items.append(value)
                        start_index += len(items)   

                    

            
            # ไม่มี local_id        
            if not flag_chk and not local_id:
                # Access the 'pagemap' dictionary within the item
                pagemap = item.get('pagemap', {})

                # Access the 'thumbnail' list within the pagemap
                cse_image = pagemap.get('cse_image', [])

                # Iterate through each thumbnail in the list
                for thumbnail in cse_image:

                    # Access the 'src' value within the thumbnail
                    img = thumbnail.get('src', '')
                    if img.startswith('https://') and img and is_image(img):
                        
                        favorite = {
                            "favId": str(uuid.uuid4()),
                            'img': img,
                            "title": recipe_name,
                            'url': item_link,
                            'title': title,
                            "isFavorite": 'None',
                            "userId": 'None'
                            # Add more fields as needed
                        }

                        menu_items.append(favorite)
                        start_index += len(items)   
                 
    return menu_items[:total_results]  # Return up to the specified total_results

class LinkResource(Resource):
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

            menu_items = retrieve_menu_items_link(api_key, recipe_name,10,localId)
           

            response = {
                "status": "1",
                "message": "Data retrieved successfully",
                "data": menu_items
            }
            return response, 200
 


        

        except NameError:
                traceback.print_exc(limit=1)  # Print the traceback with limit 1 to only show the line that raised the exception
                print("Variable 'my_variable' is not defined.")
        except Exception as e:
            # Handle the exception and return an appropriate response
            error_message = f"An error occurred: {str(e)}"
            return {"error": error_message}, 500
