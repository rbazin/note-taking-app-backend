# Note taking app backend

Frontend part of the Natural Voice Commands note-taking application for the Visually Impaired. Intended as a final graduate project for the Human Computer Interaction course at McGill University. Find frontend [here](https://github.com/rbazin/note-taking-app-frontend).

## Installation

Requires python 3.11, install dependencies with :

```bash
pip install -r requirements.txt
```

This project also requires you to create a .env file in the root folder, containing your OpenAI API key.

## Start the development server

```bash
uvicorn main:app --reload --port 5000
```
