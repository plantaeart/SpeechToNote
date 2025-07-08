# Speech to Note 💬📝

## Description 📒
This project will help me put everything together with a new stack i want to test ! And also i wanted to have a web app that will create note with speech :
* The __speaker__ tell things about it's note
* He could also structured it's note with the following speech __point <element> point__
* Those elements could be :
  * Title
  * Sub Title
  * Separator
  * List
  * etc...
* To stop a note, the __speaker__ will need to say __point end point__
* All those command could be updated to other command type
At the end the __speaker__ will be able to review the note and modify it by hand

## Project stack 🎯
### Backend
* Python (https://www.python.org) - Programing langage - version 3.13.3
* FastAPI (https://fastapi.tiangolo.com) - A modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints - version 0.115.4
* Uvicorn (https://www.uvicorn.org) - ASGI web server implementation for Python - version 0.32.0
* Pymongo (https://pymongo.readthedocs.io/en/stable/) - A Python distribution containing tools for working with MongoDB - version 4.10.1
* Pydantic (https://docs.pydantic.dev/latest/) - The most widely used data validation library for Python - version 2.9.2

### Frontend
* VueJS (https://vuejs.org) - An approachable, performant and versatile framework for building web user interfaces - version 3.5.17
* Pinia (https://pinia.vuejs.org/introduction.html) - A store library for Vue, it allows you to share a state across components/pages - version 3.0.3

### DB
* MongoDB official docker image (https://hub.docker.com/_/mongo) - MongoDB is a free and open-source cross-platform document-oriented database⁠ program. Classified as a NoSQL⁠ database program - version 6.0
* DuckDB (https://duckdb.org) - DuckDB is a fast analitycal database system - version 1.3.1

### Contenerization
* Kubernetes
* Docker

## Steps 🪜
🟩 : Done 🟧 : In progress 🟪 : To do

* Create the project
* Init the FastAPI backend 🟩
  * Create the speaker note model 🟩
  * Create the spaker note routes 🟩
  * Create the speaker command model 🟩
  * Create the speaker command routes 🟩
  * Test it manually 🟩
  * Create automatic tests 🟧
* Init the VueJS frontend (with Pinia) 🟩
  * Create the models services 🟪
  * Create the pinia stores 🟪
* Init the mongodb local docker 🟩
