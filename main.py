from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import base64
import wave
import subprocess
import os

import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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

class Audio(BaseModel):
    audio_b64: str

@app.post("/transcribe")
async def transcribe(audio: Audio):
    # save audio to disk
    audio_b64 = audio.audio_b64.split(",")[1]
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
        transcript = transcript.strip()
    
    # remove temporary files
    os.remove("audio.wav")
    os.remove("transcript.txt")

    return {"transcript": f"{transcript}", "notes": f"{transcript}"}