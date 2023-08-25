# Note taking app backend

Beckend for the natural voice commands note-taking app, powered by whisper, langchain and GPT-3.5

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
