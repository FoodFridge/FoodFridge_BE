import pyrebase
from pyrebase import auth



firebaseConfig = {
                'apiKey': "AIzaSyBq5lsZOZoMmhdMMI2CLJsLxwH-QpEwirk",
                'authDomain': "foodfridge-617b1.firebaseapp.com",
                'databaseURL': "https://foodfridge-617b1-default-rtdb.firebaseio.com",
                'projectId': "foodfridge-617b1",
                'storageBucket': "foodfridge-617b1.appspot.com",
                'messagingSenderId': "664643258545",
                'appId': "1:664643258545:web:04a8b0d3c6a856a5737a90",
                'measurementId': "G-1XF57EL9ES"
}

firebase=pyrebase.initialize_app(firebaseConfig)
auth-firebase.auth()

def login():
    pass

def signup():
    print("Sign Up...")
    email = input("Enter Email: " )
    password = input("Enter Password: " )
    try:
        user = auth.create_user_with_email_and_password(email, password)
    except: 
        print("email is already exist")
    return

ans = input("Are you new user?[y,n]")

if ans =='n':
    login()
elif ans =="y":
    signup()