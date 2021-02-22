# Full Stack API Final Project

## Full Stack Trivia

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game, The application has the ability to:

1) Display questions - both all questions and by category. Questions shows the question, category and difficulty rating by default and can show/hide the answer. 
2) Delete questions.
3) Add questions and require that they include question and answer text.
4) Search for questions based on a text query string.
5) Play the quiz game, randomizing either all questions or within a specific category. 


### Installing Dependencies

#### Installing Node and NPM

This project depends on Nodejs and Node Package Manager (NPM). Before continuing, you must download and install Node (the download includes NPM) from [https://nodejs.com/en/download](https://nodejs.org/en/download/).

#### Installing project dependencies

This project uses NPM to manage software dependencies. NPM Relies on the package.json file located in the `frontend` directory of this repository. After cloning, open your terminal and run: `npm install`


#### Database Setup

`trivia.psql` file was provided as a part of the starter code. It has been restored to the `trivia` database backend folder by running the following command in the terminal:

`psql trivia < trivia.psql`

## About the Stack

The full stack application is desiged with some key functional areas:

### Backend

The `./backend` directory contains the completed Flask and SQLAlchemy server. The endpoints have been defined in the `__init__.py` to define the endpoints and models.py for DB and SQLAlchemy setup are referenced as needed. 

### Frontend

The `./frontend` directory contains a complete React frontend to consume the data from the Flask server with updated endpoints 

### API Reference

Base URL: Currently the trivia application is hosted locally. The backend is hosted at http://127.0.0.1:5000/

Authentication: Current version does not require any authentication or API keys.

### Running the server

From within the backend directory first ensure you are working using your created virtual environment.

To run the server in linux environment, execute:

`export FLASK_APP=flaskr`
`export FLASK_ENV=development`
`flask run`

To run the server in thw windows environment, execute:

`set FLASK_APP=flaskr`
`set FLASK_ENV=development`
`flask run`

## Running Your Frontend in Dev Mode

The frontend app was built using create-react-app. In order to run the app in development mode use ```npm start```. You can change the script in the ```package.json``` file. 

Open [http://localhost:3000](http://localhost:3000) to view it in the browser. The page will reload if you make edits.<br>


`npm start`

### Getting Started

Backend Base URL: http://127.0.0.1:5000/
Frontend Base URL: http://127.0.0.1:3000/

### Error Handling

Errors are returned as JSON objects in the following format:

{
    "success": False, 
    "error": 400,
    "message": "bad request"
}

The API will return three error types when requests fail:

400: Bad Request
404: Resource Not Found
405: Method Not Allowed
422: Not Processable

### EndPoints

GET/categories:


{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "success": true,
    "total_categories": 6
}


GET/questions

{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "current_category": null,
    "questions": [
        {
            "answer": "The Liver",
            "category": 1,
            "difficulty": 4,
            "id": 20,
            "question": "What is the heaviest organ in the human body?"
        },
        {
            "answer": "Alexander Fleming",
            "category": 1,
            "difficulty": 3,
            "id": 21,
            "question": "Who discovered penicillin?"
        },
        {
            "answer": "Blood",
            "category": 1,
            "difficulty": 4,
            "id": 22,
            "question": "Hematology is a branch of medicine involving the study of what?"
        },
        {
            "answer": "Jupiter",
            "category": 1,
            "difficulty": 3,
            "id": 39,
            "question": "What is the largest planet in the solar system?"
        },
        {
            "answer": "AB negative",
            "category": 1,
            "difficulty": 3,
            "id": 40,
            "question": "What is the rarest blood type?"
        },
        {
            "answer": "Tendons",
            "category": 1,
            "difficulty": 3,
            "id": 41,
            "question": "What tissues connect the muscles to the bones?"
        },
        {
            "answer": "Escher",
            "category": 2,
            "difficulty": 1,
            "id": 16,
            "question": "Which Dutch graphic artist initials M C was a creator of optical illusions?"
        },
        {
            "answer": "Mona Lisa",
            "category": 2,
            "difficulty": 3,
            "id": 17,
            "question": "La Giaconda is better known as what?"
        },
        {
            "answer": "One",
            "category": 2,
            "difficulty": 4,
            "id": 18,
            "question": "How many paintings did Van Gogh sell in his lifetime?"
        },
        {
            "answer": "Jackson Pollock",
            "category": 2,
            "difficulty": 2,
            "id": 19,
            "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
        }
    ],
    "status_code": 200,
    "success": true,
    "total_questions": 25
}