"""Application constants."""

class PredictionTask:
    EMOTION = "emotion"
    SENTIMENT = "sentiment"
    INTENT = "intent"
    STRESS = "stress"
    URGENCY = "urgency"
    TOXICITY = "toxicity"
    AGGRESSION = "aggression"
    POLITENESS = "politeness"
    TRUST_SCORE = "trust_score"
    CSAT = "customer_satisfaction"
    CHURN_RISK = "churn_risk"
    BUYING_PROBABILITY = "buying_probability"
    CONVERSATION_QUALITY = "conversation_quality"
    BIG_FIVE = "big_five"
    BURNOUT_RISK = "burnout_risk"
    COMMUNICATION_STYLE = "communication_style"

ALL_PREDICTION_TASKS = [v for k, v in vars(PredictionTask).items() if not k.startswith("_")]