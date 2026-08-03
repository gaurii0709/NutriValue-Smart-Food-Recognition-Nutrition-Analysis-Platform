from app.utils.nutrition_data import FOOD_NUTRITION
from app.utils.question_engine import calculate_nutrition as calculate_engine
from typing import Dict, List, Any, Optional


class NutritionService:
    """Service to handle all nutrition-related operations"""

    @staticmethod
    def get_food_questions(food_name: str) -> Optional[Dict]:
        """
        Get questions and base nutrition for a food item

        Args:
            food_name: Name of the food (e.g., 'pizza', 'burger')

        Returns:
            Dict with food data or None if not found
        """
        food = FOOD_NUTRITION.get(food_name.lower())

        if food:
            return {
                'success': True,
                'food': food_name,
                'display_name': food_name.replace('_', ' ').title(),
                'questions': food['questions'],
                'base_nutrition': food['base_nutrition'],
                'total_questions': len(food['questions'])
            }
        else:
            # Fallback for unknown foods
            return {
                'success': False,
                'food': food_name,
                'message': 'Food not found in database',
                'questions': [
                    {
                        'question': 'What is the portion size?',
                        'options': ['Small', 'Medium', 'Large'],
                        'multiplier': {'Small': 0.7, 'Medium': 1.0, 'Large': 1.3}
                    }
                ],
                'base_nutrition': {
                    'calories': 200,
                    'protein': 5,
                    'carbs': 20,
                    'fat': 10,
                    'fiber': 1
                }
            }

    @staticmethod
    def calculate_nutrition(food_name: str, answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate nutrition based on user answers

        Args:
            food_name: Name of the food
            answers: Dictionary of question_id -> answer

        Returns:
            Calculated nutrition values
        """
        # Use the existing calculate function from question_engine
        nutrition = calculate_engine(food_name, answers)

        # Add metadata
        nutrition['food'] = food_name
        nutrition['calculated_at'] = '2026-03-02'

        # Add confidence level based on how many questions answered
        food = FOOD_NUTRITION.get(food_name.lower())
        if food:
            total_q = len(food['questions'])
            answered_q = len(answers)
            confidence = min(1.0, answered_q / max(1, total_q))

            if confidence > 0.8:
                nutrition['confidence'] = 'high'
            elif confidence > 0.5:
                nutrition['confidence'] = 'medium'
            else:
                nutrition['confidence'] = 'low'
        else:
            nutrition['confidence'] = 'low'

        return nutrition

    @staticmethod
    def get_all_foods() -> List[str]:
        """Get list of all available foods"""
        return list(FOOD_NUTRITION.keys())

    @staticmethod
    def validate_answers(food_name: str, answers: Dict) -> Dict:
        """
        Validate if all required questions are answered

        Returns:
            Dict with validation result
        """
        food = FOOD_NUTRITION.get(food_name.lower())
        if not food:
            return {
                'valid': False,
                'missing': [],
                'message': 'Food not found'
            }

        # Check required questions (you can mark some as required)
        required_indices = [0]  # By default, first question is required

        missing = []
        for idx in required_indices:
            if str(idx) not in answers:
                missing.append(food['questions'][idx]['question'])

        return {
            'valid': len(missing) == 0,
            'missing': missing,
            'total_questions': len(food['questions']),
            'answered': len(answers)
        }


# Create a singleton instance
nutrition_service = NutritionService(\
    )