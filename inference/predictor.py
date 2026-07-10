"""Main predictor using HuggingFace models."""

import asyncio
from typing import List, Dict, Any
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

from configs.settings import settings
from utils.logger import get_logger
from core.constants import ALL_PREDICTION_TASKS

logger = get_logger(__name__)


class Predictor:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        self.models = {}
        self.tokenizers = {}
        self._load_models()

    def _load_models(self):
        """Load all required HuggingFace models."""
        # Map task to model name (simplified)
        task_to_model = {
            "sentiment": "distilbert-base-uncased-finetuned-sst-2-english",
            "emotion": "bhadresh-savani/bert-base-uncased-emotion",
            "toxicity": "unitary/toxic-bert",
            # ... many more
        }
        for task, model_name in task_to_model.items():
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForSequenceClassification.from_pretrained(model_name)
                self.tokenizers[task] = tokenizer
                self.models[task] = pipeline(
                    "text-classification",
                    model=model,
                    tokenizer=tokenizer,
                    device=self.device,
                    return_all_scores=True,
                )
                logger.info(f"Loaded model for {task}")
            except Exception as e:
                logger.error(f"Failed to load model for {task}: {e}")

    def available_tasks(self) -> List[str]:
        return list(self.models.keys())

    async def predict(self, text: str, tasks: List[str]) -> Dict[str, Any]:
        """Run prediction for given tasks."""
        loop = asyncio.get_event_loop()
        results = {}
        for task in tasks:
            if task not in self.models:
                continue
            # Run in thread to avoid blocking
            result = await loop.run_in_executor(
                None, self.models[task], text
            )
            # Parse result
            # For classification, result is list of dicts with label, score
            # We'll simplify to top label and confidence
            top = max(result[0], key=lambda x: x["score"])
            results[task] = {
                "label": top["label"],
                "confidence": top["score"],
                "all_scores": result[0],
            }
        return results