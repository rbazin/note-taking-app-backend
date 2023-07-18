from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import get_chain

import base64
import wave
import subprocess
import json
import os

app = FastAPI()

origins = [
    "http://notes.romain-bazin.com",
    "https://notes.romain-bazin.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel):
    # TODO : change notes from str to dict
    notes_tree: str
    audio_b64: str

@app.post("/transcribe")
async def transcribe(req: Request):
    # TODO : change notes from str to dict
    notes_str = json.load(req.notes_tree)
    notes_str = json.dumps(notes_str, indent=2)
    audio_b64 = req.audio_b64.split(",")[1]
    audio = base64.b64decode(audio_b64)

    with wave.open("audio.wav", "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(audio)

    # trascribe audio
    subprocess.run(["./whisper.cpp/main",
                    "-f", "audio.wav", 
                    "-m", "./whisper.cpp/models/ggml-small.bin",
                    "--no-timestamps",
                    "--language", "auto",
                    "--output-txt",
                    "--output-file", "transcript"])
    
    # read transcript
    with open("transcript.txt", "r") as f:
        transcript = f.read()
        instructions = transcript.strip()
    
    # remove temporary files
    os.remove("audio.wav")
    os.remove("transcript.txt")

    # instruction understanding with agent
    chain = get_chain()
    new_notes_tree = chain.run(notes_tree=notes_str, instructions=instructions)
    new_notes_tree = json.loads(new_notes_tree)

    return {"transcript": f"{instructions}", "new_notes": new_notes_tree}