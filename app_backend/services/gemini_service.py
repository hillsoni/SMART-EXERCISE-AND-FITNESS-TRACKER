import google.generativeai as genai
import os

class GeminiService:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')

    def generate_diet_plan(self, user_data):
        """Generate personalized diet plan using Gemini"""
        prompt = f"""
        Create a detailed diet plan for:
        Age: {user_data['age']}
        Gender: {user_data['gender']}
        Weight: {user_data['weight']} kg
        Height: {user_data['height']} cm
        Activity Level: {user_data['activity_level']}
        Goal: {user_data['goal']}
        Diet Type: {user_data['diet_type']}
        Health Conditions: {user_data.get('health_conditions', [])}

        Provide a complete daily meal plan with breakfast, lunch, snack, and dinner.
        Include calorie counts and nutritional information.
        """
        response = self.model.generate_content(prompt)
        return response.text

    def chat_response(self, question, context="diet"):
        """Generate chatbot response - restricted to diet topics"""
        if context != "diet":
            return "I can only answer questions related to diet and nutrition."

        prompt = f"""
        As a professional nutritionist, answer this question:
        {question}

        Provide accurate, helpful information about diet and nutrition.
        """
        response = self.model.generate_content(prompt)
        return response.text

    def suggest_challenges(self, user_data):
        """Generate personalized fitness challenges using Gemini"""
        prompt = f"""
        As a professional fitness trainer, suggest 5-10 personalized fitness challenges based on the following user information:
        
        Age: {user_data.get('age', 'Not provided')}
        Gender: {user_data.get('gender', 'Not provided')}
        Weight: {user_data.get('weight', 'Not provided')} kg
        Height: {user_data.get('height', 'Not provided')} cm
        Activity Level: {user_data.get('activity_level', 'Not provided')}
        Goal: {user_data.get('goal', 'Not provided')}
        
        For each challenge, provide:
        1. Title (e.g., "30-Day Push-Up Challenge")
        2. Type (Strength, Core, Cardio, Flexibility, Mindfulness, Stamina)
        3. Duration (e.g., "30 Days", "7 Days", "21 Days")
        4. Difficulty (Beginner, Intermediate, Advanced)
        5. Goal (Weight Loss, Weight Gain, Strength, Core Strength, Maintain Fitness, Trauma Recovery)
        6. Brief description
        
        Format the response as a JSON array of objects with these exact keys:
        title, type, duration, difficulty, goal, description
        
        Example format:
        [
            {{
                "title": "30-Day Push-Up Challenge",
                "type": "Strength",
                "duration": "30 Days",
                "difficulty": "Intermediate",
                "goal": "Strength",
                "description": "Build upper body strength with progressive push-up training"
            }},
            ...
        ]
        
        Return ONLY the JSON array, no additional text.
        """
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            import json
            import re
            text = response.text.strip()
            # Try to extract JSON array from the response
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                challenges_json = json.loads(json_match.group())
                return challenges_json
            else:
                # Fallback: try to parse the entire response
                return json.loads(text)
        except Exception as e:
            # Fallback to default challenges if AI fails
            return [
                {
                    "title": "30-Day Push-Up Challenge",
                    "type": "Strength",
                    "duration": "30 Days",
                    "difficulty": "Intermediate",
                    "goal": "Strength",
                    "description": "Build upper body strength with progressive push-up training"
                },
                {
                    "title": "7-Day Core Challenge",
                    "type": "Core",
                    "duration": "7 Days",
                    "difficulty": "Beginner",
                    "goal": "Core Strength",
                    "description": "Strengthen your core muscles with daily core exercises"
                }
            ]