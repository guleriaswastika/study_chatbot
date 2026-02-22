import datetime
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pymongo import MongoClient
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
app = FastAPI() 
client = ChatGroq(
    api_key="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"
  model="llama3-8b-8192"  
)
@app.get("/")
def read_root():
    return {"message":"app is running"}
load_dotenv(".env")
groq_api_key = os.getenv("GROQ_API_KEY")
print("LOADED KEY:", groq_api_key)
mongo_uri = os.getenv("MONGODB_URI")
Print("loaded GROQ KEY:", groq_api_key)
print("loaded mongo URI:", mongo_uri)

client = MongoClient(mongo_uri)
db = client["chat"]
collection = db["users"]

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    question: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "you are a study bot , give me the output accordingly"),
        ("placeholder", "{history}"),
        ("user", "{question}")
    ]
)

llm = ChatGroq(api_key = groq_api_key, model="llama3-8b-8192") 
chain = prompt | llm

def get_history(user_id):
    chats = collection.find({"user_id": user_id}).sort("timestamp", 1)
    history = []

    for chat in chats:
        history.append((chat["role"], chat["message"]))
    return history

@app.get("/") 
def home():
    return {"message": "Welcome study Chatbot API!"}

@app.post("/chat")
def chat(request: ChatRequest):
    history = get_history(request.user_id)
    response = chain.invoke({"history": history, "question": request.question})

    collection.insert_one({
        "user_id": request.user_id,
        "role": "user",
        "message": request.question,
        "timestamp": datetime.utcnow()
    })

    collection.insert_one({
        "user_id": request.user_id,
        "role": "assistant",
        "message": response.content,
        "timestamp": datetime.utcnow()
    })

    return {"response" : response.content} 