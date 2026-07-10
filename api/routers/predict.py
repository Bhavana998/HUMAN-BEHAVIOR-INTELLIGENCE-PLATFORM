from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from transformers import pipeline

router = APIRouter()

# Load models (they download on first use)
print("Loading sentiment model...")
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

print("Loading emotion model...")
emotion_pipeline = pipeline("text-classification", model="bhadresh-savani/bert-base-uncased-emotion", return_all_scores=False)

print("Loading toxicity model...")
toxicity_pipeline = pipeline("text-classification", model="unitary/toxic-bert", return_all_scores=False)

print("All models loaded successfully!")

class PredictionRequest(BaseModel):
    text: str
    tasks: List[str] = ["sentiment"]

class PredictionResponse(BaseModel):
    text: str
    results: dict

@router.post("/single", response_model=PredictionResponse)
async def predict_single(request: PredictionRequest):
    text = request.text
    results = {}
    
    # Sentiment
    if "sentiment" in request.tasks:
        result = sentiment_pipeline(text)[0]
        results["sentiment"] = {
            "label": result["label"],
            "score": result["score"]
        }
    
    # Emotion
    if "emotion" in request.tasks:
        result = emotion_pipeline(text)[0]
        results["emotion"] = {
            "label": result["label"],
            "score": result["score"]
        }
    
    # Toxicity
    if "toxicity" in request.tasks:
        result = toxicity_pipeline(text)[0]
        results["toxicity"] = {
            "label": result["label"],
            "score": result["score"]
        }
    
    return PredictionResponse(text=text, results=results)