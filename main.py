from fastapi import FastAPI

app = FastAPI()


@app.post("/transcribe")
async def transcribe():
    return {"message": "Hello World"}