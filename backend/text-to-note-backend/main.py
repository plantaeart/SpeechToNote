from fastapi import FastAPI
from pymongo import MongoClient

app = FastAPI()


"""

http://127.0.0.1:8000/docs pour le Swagger

"""

@app.get("/")
async def root():
    return {"message": "Hello World"}