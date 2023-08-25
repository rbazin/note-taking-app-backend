from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from agent import get_chain

import base64
import wave
import subprocess
import json
import os
import re

app = FastAPI()

origins = [
    # Insert your url here
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

def parse_json(text: str) -> dict | None:
    """ Greedly recovers the first occurence of a JSON object in a string """
    pattern = r"```json\s+(.*?)\s+```"
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        json_str = match.group(1)
        json_obj = json.loads(json_str)
        return json_obj
    else:
        return None


class Notes(BaseModel):
    id: int
    name: str
    type: str
    text: str | None
    children: List["Notes"]

class Request(BaseModel):
    notes: Notes
    audio_b64: str

@app.post("/transcribe")
async def transcribe(req: Request):
    # get notes
    notes = req.notes.dict()
    print(notes)

    # notes_str = json.load(req.notes)
    notes_str = json.dumps(notes, indent=2)
    print(notes_str)
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
                    "-m", "./whisper.cpp/models/ggml-medium.en-q5_0.bin",
                    "--no-timestamps",
                    "--language", "en",
                    #"--translate",
                    "--output-txt",
                    "--output-file", "transcript"])
    
    with open("transcript.txt", "r") as f:
        transcript = f.read()
        instructions = transcript.strip()
    
    # remove temporary files
    os.remove("audio.wav")
    os.remove("transcript.txt")

    # instruction understanding with agent
    chain = get_chain(model="gpt-3.5-turbo")
    try:
        new_notes_tree = chain.run(notes_tree=notes_str, instructions=instructions)
        print("New notes :")
        print(new_notes_tree)
        new_notes_tree = parse_json(new_notes_tree)
        for i in range(3):
            if new_notes_tree is None:
                print("New notes :")
                print(new_notes_tree)
                new_notes_tree = chain.run(notes_tree=notes_str, instructions=instructions)
                new_notes_tree = parse_json(new_notes_tree)
            else:
                break
    except Exception as e:
        print(e)
        return {"transcript": f"{instructions}"}, 500
    if new_notes_tree is None:
        return {"transcript": f"{instructions}"}, 500

    return {"transcript": f"{instructions}", "new_notes": new_notes_tree}