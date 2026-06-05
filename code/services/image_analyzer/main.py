from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Image Analyzer Service")


class ImageInput(BaseModel):
    image_url: str


@app.get("/")
def root():
    return {"message": "Image Analyzer Service Running"}


@app.post("/analyse")
def analyse_image(data: ImageInput):
    image_url = data.image_url.lower()

    if "kitchen" in image_url:
        room_type = "kitchen"
        condition_score = 4
        confidence = 0.90

    elif "bathroom" in image_url:
        room_type = "bathroom"
        condition_score = 3
        confidence = 0.85

    elif "bedroom" in image_url:
        room_type = "bedroom"
        condition_score = 4
        confidence = 0.88

    elif "living" in image_url:
        room_type = "living room"
        condition_score = 4
        confidence = 0.86

    elif "exterior" in image_url:
        room_type = "exterior"
        condition_score = 3
        confidence = 0.82

    else:
        room_type = "other"
        condition_score = 2
        confidence = 0.60

    return {
        "room_type": room_type,
        "condition_score": condition_score,
        "confidence": confidence
    }