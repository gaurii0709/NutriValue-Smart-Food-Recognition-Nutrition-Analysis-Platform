import numpy as np
import random
import json
import os
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from typing import Dict, List, Any


class SmartQuestionClassifier:
    """Smart classifier with question system and actual ML model"""

    def __init__(self):
        self.categories = [
            "flatbreads",
            "rice_dishes",
            "curries",
            "savory_snacks",
            "sweets_desserts"
        ]

        # Your 7 working classes (in alphabetical order)
        self.class_names = ['cheesecake', 'french_fries', 'fried_rice', 'hamburger', 'ice_cream', 'pizza', 'samosa']

        # Confidence threshold for unknown foods (65%)
        self.CONFIDENCE_THRESHOLD = 0.65

        # Map to display names
        self.display_names = {
            'cheesecake': 'Cheesecake',
            'french_fries': 'French Fries',
            'fried_rice': 'Fried Rice',
            'hamburger': 'Hamburger',
            'ice_cream': 'Ice Cream',
            'pizza': 'Pizza',
            'samosa': 'Samosa'
        }

        # Emoji mapping
        self.emoji_map = {
            'cheesecake': '🍰',
            'french_fries': '🍟',
            'fried_rice': '🍚',
            'hamburger': '🍔',
            'ice_cream': '🍦',
            'pizza': '🍕',
            'samosa': '🥟'
        }

        # Category mapping for questions
        self.food_to_category = {
            'pizza': 'flatbreads',
            'hamburger': 'savory_snacks',
            'fried_rice': 'rice_dishes',
            'ice_cream': 'sweets_desserts',
            'cheesecake': 'sweets_desserts',
            'samosa': 'savory_snacks',
            'french_fries': 'savory_snacks'
        }

        # Try to load actual ML model
        self.model = None
        self.model_loaded = False
        self._load_model()

        # Complete Question Database
        self.question_db = self._create_question_database()

    def _load_model(self):
        """Load the trained Keras model"""
        try:
            # Load the 7-food model
            model_path = os.path.join(os.path.dirname(__file__), '../../../ml_model/food_model_7_foods.keras')
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                self.model_loaded = True
                print("✅ 7-food ML Model loaded successfully!")
                print(f"✅ Model expects {self.model.output_shape[-1]} classes")
                print(f"✅ Confidence threshold: {self.CONFIDENCE_THRESHOLD * 100}%")
                if self.model.output_shape[-1] == 7:
                    print("✅ Model has 7 classes - perfect for your 7 foods!")
                else:
                    print(f"⚠️ Warning: Model has {self.model.output_shape[-1]} classes, but expected 7")
            else:
                print(f"⚠️ Model not found at {model_path}, using mock predictions")
                print(f"Current path: {os.path.dirname(__file__)}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("⚠️ Using mock predictions")

    def _create_question_database(self) -> Dict[str, List[Dict]]:
        """Create comprehensive question database"""
        return {
            "flatbreads": [
                {
                    "id": "size",
                    "question": "🍕 What size pizza?",
                    "options": ["Small (6 slices)", "Medium (8 slices)", "Large (10 slices)"],
                    "multiplier": {"Small (6 slices)": 0.7, "Medium (8 slices)": 1.0, "Large (10 slices)": 1.3}
                },
                {
                    "id": "crust",
                    "question": "🥖 What crust type?",
                    "options": ["Thin Crust", "Regular Crust", "Stuffed Crust"],
                    "multiplier": {"Thin Crust": 0.8, "Regular Crust": 1.0, "Stuffed Crust": 1.3}
                },
                {
                    "id": "toppings",
                    "question": "🧀 Any extra toppings?",
                    "options": ["No extras", "Extra cheese", "Extra veggies", "Pepperoni"],
                    "additions": {"No extras": 0, "Extra cheese": 50, "Extra veggies": 20, "Pepperoni": 80}
                },
                {
                    "id": "slices",
                    "question": "🔪 How many slices did you eat?",
                    "options": ["1 slice", "2 slices", "3 slices", "4 slices", "Whole pizza"],
                    "multiplier": {"1 slice": 0.125, "2 slices": 0.25, "3 slices": 0.375, "4 slices": 0.5,
                                   "Whole pizza": 1.0}
                }
            ],

            "rice_dishes": [
                {
                    "id": "type",
                    "question": "🍚 What type of fried rice?",
                    "options": ["Vegetable", "Egg", "Chicken", "Shrimp"],
                    "additions": {"Vegetable": 0, "Egg": 70, "Chicken": 120, "Shrimp": 110}
                },
                {
                    "id": "portion",
                    "question": "🥣 Portion size?",
                    "options": ["Small bowl", "Regular bowl", "Large bowl"],
                    "multiplier": {"Small bowl": 0.7, "Regular bowl": 1.0, "Large bowl": 1.4}
                },
                {
                    "id": "oil",
                    "question": "🫒 Oil level?",
                    "options": ["Less oil", "Regular", "Extra oil"],
                    "multiplier": {"Less oil": 0.8, "Regular": 1.0, "Extra oil": 1.3}
                },
                {
                    "id": "quantity",
                    "question": "🔢 How many cups?",
                    "type": "number",
                    "min": 0.5,
                    "max": 4,
                    "default": 1,
                    "multiplier": "direct"
                }
            ],

            "savory_snacks": [
                {
                    "id": "type",
                    "question": "🍔 What type of burger?",
                    "options": ["Chicken", "Beef", "Veggie"],
                    "multiplier": {"Chicken": 1.0, "Beef": 1.2, "Veggie": 0.9}
                },
                {
                    "id": "patty",
                    "question": "🥩 How many patties?",
                    "options": ["Single", "Double", "Triple"],
                    "multiplier": {"Single": 1.0, "Double": 1.8, "Triple": 2.5}
                },
                {
                    "id": "cheese",
                    "question": "🧀 With cheese?",
                    "options": ["No cheese", "With cheese"],
                    "additions": {"No cheese": 0, "With cheese": 50}
                },
                {
                    "id": "fries",
                    "question": "🍟 With fries?",
                    "options": ["No fries", "Small fries", "Large fries"],
                    "additions": {"No fries": 0, "Small fries": 220, "Large fries": 400}
                },
                {
                    "id": "samosa_quantity",
                    "question": "🥟 How many samosas?",
                    "options": ["1", "2", "3", "4", "5"],
                    "multiplier": {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}
                },
                {
                    "id": "samosa_filling",
                    "question": "🥔 Samosa filling?",
                    "options": ["Aloo (Potato)", "Keema (Meat)", "Mix"],
                    "additions": {"Aloo (Potato)": 0, "Keema (Meat)": 60, "Mix": 30}
                },
                {
                    "id": "fries_size",
                    "question": "🍟 French fries size?",
                    "options": ["Small", "Medium", "Large"],
                    "multiplier": {"Small": 0.6, "Medium": 1.0, "Large": 1.5}
                }
            ],

            "sweets_desserts": [
                {
                    "id": "type",
                    "question": "🍦 What type?",
                    "options": ["Ice Cream", "Cheesecake"],
                    "multiplier": {"Ice Cream": 1.0, "Cheesecake": 1.5}
                },
                {
                    "id": "scoops",
                    "question": "🍦 How many scoops?",
                    "options": ["1 scoop", "2 scoops", "3 scoops"],
                    "multiplier": {"1 scoop": 1.0, "2 scoops": 2.0, "3 scoops": 3.0}
                },
                {
                    "id": "flavor",
                    "question": "🎨 What flavor?",
                    "options": ["Vanilla", "Chocolate", "Strawberry", "Mango"],
                    "additions": {"Vanilla": 0, "Chocolate": 15, "Strawberry": 5, "Mango": 5}
                },
                {
                    "id": "toppings",
                    "question": "🍬 Any toppings?",
                    "options": ["No", "Chocolate syrup", "Sprinkles", "Nuts"],
                    "additions": {"No": 0, "Chocolate syrup": 40, "Sprinkles": 20, "Nuts": 60}
                },
                {
                    "id": "cheesecake_slices",
                    "question": "🍰 How many slices?",
                    "options": ["1", "2"],
                    "multiplier": {"1": 1, "2": 2}
                }
            ]
        }

    def _preprocess_image(self, image_path):
        """Preprocess image for model prediction"""
        try:
            img = image.load_img(image_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            return img_array / 255.0
        except Exception as e:
            print(f"❌ Error preprocessing image: {e}")
            return None

    def predict_category(self, image_path: str = None) -> Dict[str, Any]:
        """
        Predict food category from image using the trained model
        With confidence threshold for unknown foods
        """
        if image_path and self.model_loaded:
            try:
                # Preprocess image
                img_array = self._preprocess_image(image_path)
                if img_array is None:
                    return self._mock_prediction()

                # Make prediction
                predictions = self.model.predict(img_array, verbose=0)[0]

                # Get top prediction
                predicted_index = np.argmax(predictions)
                predicted_class = self.class_names[predicted_index]
                confidence = float(predictions[predicted_index])

                # Get top 3 predictions for debugging
                top_3_idx = np.argsort(predictions)[-3:][::-1]
                top_3 = [(self.class_names[i], float(predictions[i])) for i in top_3_idx]

                # Get category for questions
                predicted_category = self.food_to_category.get(predicted_class, 'savory_snacks')

                print(f"✅ Model predicted: {predicted_class} ({confidence:.2f}) -> Category: {predicted_category}")
                print(f"📊 Top 3: {top_3}")

                # CONFIDENCE THRESHOLD - Check if confidence is too low
                if confidence < self.CONFIDENCE_THRESHOLD:
                    print(f"⚠️ Confidence {confidence:.2f} below threshold {self.CONFIDENCE_THRESHOLD}. Marking as UNKNOWN.")
                    return {
                        "category": "unknown",
                        "food": "unknown",
                        "display_name": "Unknown Food",
                        "emoji": "❓",
                        "confidence": confidence,
                        "is_mock": False,
                        "is_unknown": True,
                        "message": "Could not identify food confidently. Please try another photo or select from our 7 supported foods."
                    }

                return {
                    "category": predicted_category,
                    "food": predicted_class,
                    "display_name": self.display_names.get(predicted_class, predicted_class.replace('_', ' ').title()),
                    "emoji": self.emoji_map.get(predicted_class, '🍽️'),
                    "confidence": confidence,
                    "top_3": top_3,
                    "is_mock": False,
                    "is_unknown": False
                }

            except Exception as e:
                print(f"❌ Prediction error: {e}")
                return self._mock_prediction()
        else:
            return self._mock_prediction()

    def _mock_prediction(self) -> Dict[str, Any]:
        """Mock prediction for when model isn't available"""
        foods = ['pizza', 'hamburger', 'fried_rice', 'ice_cream', 'cheesecake', 'samosa', 'french_fries']
        predicted_food = random.choice(foods)
        confidence = round(random.uniform(0.8, 0.95), 2)

        category_map = {
            'pizza': 'flatbreads',
            'hamburger': 'savory_snacks',
            'fried_rice': 'rice_dishes',
            'ice_cream': 'sweets_desserts',
            'cheesecake': 'sweets_desserts',
            'samosa': 'savory_snacks',
            'french_fries': 'savory_snacks'
        }

        return {
            "category": category_map.get(predicted_food, 'savory_snacks'),
            "food": predicted_food,
            "display_name": self.display_names.get(predicted_food, predicted_food.replace('_', ' ').title()),
            "emoji": self.emoji_map.get(predicted_food, '🍽️'),
            "confidence": confidence,
            "is_mock": True,
            "is_unknown": False
        }

    def get_questions_for_category(self, category: str) -> List[Dict]:
        """Get questions for specific category"""
        return self.question_db.get(category, [])

    def calculate_nutrition(self, category: str, answers: Dict) -> Dict[str, Any]:
        """Calculate nutrition based on category and answers"""
        base_values = {
            'pizza': {'calories': 266, 'protein': 11, 'carbs': 33, 'fat': 10, 'fiber': 2, 'sugar': 3},
            'hamburger': {'calories': 295, 'protein': 17, 'carbs': 30, 'fat': 14, 'fiber': 2, 'sugar': 5},
            'fried_rice': {'calories': 150, 'protein': 4, 'carbs': 28, 'fat': 3, 'fiber': 1, 'sugar': 2},
            'ice_cream': {'calories': 207, 'protein': 4, 'carbs': 24, 'fat': 11, 'fiber': 0.5, 'sugar': 21},
            'cheesecake': {'calories': 321, 'protein': 5, 'carbs': 26, 'fat': 23, 'fiber': 0.5, 'sugar': 18},
            'samosa': {'calories': 150, 'protein': 3, 'carbs': 20, 'fat': 7, 'fiber': 1, 'sugar': 1},
            'french_fries': {'calories': 312, 'protein': 3, 'carbs': 41, 'fat': 15, 'fiber': 3, 'sugar': 0}
        }

        food_type = answers.get("type", "Unknown")

        if food_type == "Unknown" and category:
            if category == "flatbreads":
                food_type = "pizza"
            elif category == "rice_dishes":
                food_type = "fried_rice"
            elif category == "savory_snacks":
                if 'samosa' in str(answers):
                    food_type = "samosa"
                elif 'fries' in str(answers):
                    food_type = "french_fries"
                else:
                    food_type = "hamburger"
            elif category == "sweets_desserts":
                if 'cheesecake' in str(answers):
                    food_type = "cheesecake"
                else:
                    food_type = "ice_cream"

        if food_type not in base_values:
            food_type = 'pizza'

        nutrition = base_values[food_type].copy()

        total_multiplier = 1.0
        total_additions = 0

        for question_id, answer in answers.items():
            if question_id in ["quantity", "slices", "scoops", "samosa_quantity"]:
                try:
                    quantity = float(answer)
                    total_multiplier *= quantity
                except:
                    pass
            elif question_id == "cheese" and answer == "With cheese":
                total_additions += 50
            elif question_id == "fries" and "fries" in answer:
                if "Small" in answer:
                    total_additions += 220
                elif "Large" in answer:
                    total_additions += 400
                else:
                    total_additions += 320
            elif question_id == "toppings" and answer != "No" and answer != "No extras":
                if "cheese" in answer.lower():
                    total_additions += 50
                elif "veggies" in answer.lower():
                    total_additions += 20
                elif "pepperoni" in answer.lower():
                    total_additions += 80
                elif "chocolate" in answer.lower():
                    total_additions += 40
                elif "sprinkles" in answer.lower():
                    total_additions += 20
                elif "nuts" in answer.lower():
                    total_additions += 60
            elif question_id == "samosa_filling" and answer == "Keema (Meat)":
                total_additions += 60
            elif question_id == "samosa_filling" and answer == "Mix":
                total_additions += 30

        result = {
            'calories': int(nutrition['calories'] * total_multiplier + total_additions),
            'protein': round(nutrition['protein'] * total_multiplier, 1),
            'carbs': round(nutrition['carbs'] * total_multiplier, 1),
            'fat': round(nutrition['fat'] * total_multiplier, 1),
            'fiber': nutrition['fiber'],
            'sugar': round(nutrition['sugar'] * total_multiplier, 1),
            'food_type': food_type.replace('_', ' ').title(),
            'confidence': 'high' if total_multiplier == 1.0 and total_additions == 0 else 'medium'
        }

        return result


# Global instance
classifier = SmartQuestionClassifier()