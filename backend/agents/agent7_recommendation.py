import json
from groq import Groq
from core.config import settings

class RecommendationAgent:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def get_recommendations(self, state: dict) -> dict:
        # We define exactly what the frontend boxes need
        return {
            "specialist_referrals": [
                {"specialist": "Endocrinologist", "reason": "High Glucose/HbA1c management", "urgency": "High", "priority": 1}
            ],
            "lifestyle": ["30 mins brisk walking daily", "Monitor glucose every morning"],
            "dietary": ["Low carbohydrate intake", "Avoid processed sugars"],
            # THIS FILLS THE RED ALERT BOX
            "do_not_delay_if": [
                "Sudden vision changes or blurring",
                "Extreme thirst that doesn't go away",
                "Numbness or tingling in hands/feet"
            ]
        }

def generate_recommendations(state: dict) -> dict:
    agent = RecommendationAgent()
    return {**state, "recommendations": agent.get_recommendations(state)}