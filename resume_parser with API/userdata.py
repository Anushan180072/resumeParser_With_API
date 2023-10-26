from fastapi import FastAPI,Form,HTTPException,Request, Header
from starlette.responses import RedirectResponse 
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from pymongo import MongoClient
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import spacy

nlp = spacy.load("./model/model-best")
templates = Jinja2Templates(directory="templates")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["resumeParser_UserData"]
user_collection = db["users_collection"]


# Define a User model
class User:
    def __init__(self, username, email, password, confirmpassword, phonenumber, api_key):
        self.username = username
        self.email=email
        self.password = password
        self.confirmpassword=confirmpassword
        self.phonenumber=phonenumber
        self.api_key = api_key

# User registration
@app.post("/register/")
def register_user(username: str = Form(...), email: str = Form(...), password: str = Form(...), confirmpassword: str = Form(...), phonenumber: str = Form(...)):
    if user_collection.find_one({"email": email}):
        return {"message": "User already exists"}
    api_key = generate_api_key()

    # Create a user document and insert it into the collection
    user = User(username, email, password, confirmpassword, phonenumber, api_key)
    user_collection.insert_one(user.__dict__)
    return RedirectResponse(url="/login/", status_code=303)
    return {"message": "User registered successfully"}

# User login and API key issuance
@app.post("/login/")
def login_user(email: str = Form(...), password: str = Form(...)):
    user = user_collection.find_one({"email": email, "password": password})
    
    if user:
        #return {"api_key": user["api_key"]}
        response= RedirectResponse(url="/resume_parser", status_code=303)
        return response
    else:
        #raise HTTPException(status_code=401, detail="User not registered")
        redirect_response = RedirectResponse(url="/register/", status_code=303)
        return redirect_response
def generate_api_key(length=32):
    import random
    import string
    api_key = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    while user_collection.find_one({"api_key": api_key}):
        api_key = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    return api_key

@app.get("/")
async def read_root():
    return FileResponse("templates/login.html")

@app.get("/register/", status_code=200)
def display_register_page():
    return FileResponse("templates/register.html")
@app.get("/login/", status_code=200)
def display_register_page():
    return FileResponse("templates/login.html")



def get_ents(text):
    doc = nlp(text)
    res = []

    for ent in doc.ents:
        res.append({"label": ent.label_, "value": ent.text})

    return res

@app.get("/resumeparser")
def process_resume_text(text: str):
    res = get_ents(text)
    return res

@app.get("/resume_parser", response_class=HTMLResponse)
def home(req: Request):
    return templates.TemplateResponse("interface.html", {"request": req})


'''from fastapi import File, UploadFile, Form

@app.post("/resumeparser")
def process_resume_text(text: str = Form(...), resumeFile: UploadFile = File(None)):
    # Handle text and file data here
    text_data = text
    if resumeFile:
        # Process the uploaded file here
        # You can access the file's contents using resumeFile.file.read()
        file_data = resumeFile.file.read()
    else:
        file_data = None

    # Your processing logic here
    res = get_ents(text_data)
    return res

    return {"text": text_data, "file": file_data}'''



# Custom rate limiting middleware
'''@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    key = request.headers.get("API-Key")
    print(key)
    print(api_key_requests)

    if key:
        print(api_key_requests[key])
        if key in api_key_requests:
            if api_key_requests[key] >= 5:  # Change 5 to your desired limit
                # Charge the user (you can implement your billing logic here)
                charge_user(key)
                return HTTPException(status_code=429, detail="Rate limit exceeded")
            else:
                api_key_requests[key] += 1
        if key not in api_key_requests:
            api_key_requests[key] = 1

    response = await call_next(request)
    return response'''
 

'''if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)'''
