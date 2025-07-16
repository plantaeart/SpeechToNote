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
* Python (https://www.python.org) - Programing langage - __version 3.13.3__
* FastAPI (https://fastapi.tiangolo.com) - A modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints - __version 0.115.4__
* Uvicorn (https://www.uvicorn.org) - ASGI web server implementation for Python - __version 0.32.0__
* Pymongo (https://pymongo.readthedocs.io/en/stable/) - A Python distribution containing tools for working with MongoDB - __version 4.10.1__
* Pydantic (https://docs.pydantic.dev/latest/) - The most widely used data validation library for Python - __version 2.9.2__
* httpx (https://www.python-httpx.org) - HTTPX is a fully featured HTTP client for Python 3, which provides sync and async APIs, and support for both HTTP/1.1 and HTTP/2 - version __0.28.1__
* pytest (https://docs.pytest.org/en/stable/) - The pytest framework makes it easy to write small, readable tests, and can scale to support complex functional testing for applications and libraries - __version 8.4.1__
* uv (https://docs.astral.sh/uv/) - An extremely fast Python package and project manager, written in Rust - __version 0.7.21__

### DuckDB
* dotenv (https://pypi.org/project/python-dotenv/) - python-dotenv reads key-value pairs from a .env - __version 0.9.9__
* duckdb (https://duckdb.org) - DuckDB is a fast open-souce database system - __version 1.3.2__
* pandas (https://pandas.pydata.org) - A fast, powerful, flexible and easy to use open source data analysis and manipulation tool, built on top of the Python programming language - __version 2.3.1__
* Pymongo (https://pymongo.readthedocs.io/en/stable/) - A Python distribution containing tools for working with MongoDB - __version 4.10.1__

### Frontend
* VueJS (https://vuejs.org) - An approachable, performant and versatile framework for building web user interfaces - __version 3.5.17__
* Pinia (https://pinia.vuejs.org/introduction.html) - A store library for Vue, it allows you to share a state across components/pages - __version 3.0.3__

### DB
* MongoDB official docker image (https://hub.docker.com/_/mongo) - MongoDB is a free and open-source cross-platform document-oriented database⁠ program. Classified as a NoSQL⁠ database program - __version 6.0__

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
  * Create automatic tests with pyTest 🟩
* Init the VueJS frontend (with Pinia) 🟩
  * Create the models services 🟩
  * Create the pinia stores 🟩
  * Implement the business logic of record speech to text 🟩
  * Add the logic of the "commands" to structure the note 🟩
  * Make possible to edit the notes 🟩
  * Make possible to delete the notes 🟩
  * Make possible to retrieve commands 🟩
  * Make possible to edit commands 🟩
  * Make possible to add commands 🟩
* Init the mongodb local docker 🟩
* Init the fast api local docker 🟩
* Create Kubernetes environments 🟩
* Create duckdb connection to local docker mongodb 🟩
* Test duckdb operations on SPEAKER_NOTES Collections 🟩
