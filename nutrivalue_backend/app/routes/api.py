# app/routes/api.py

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import os
import json
import re
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables FIRST
load_dotenv()

# Import Supabase for authentication
try:
    from supabase import create_client, Client

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
    if supabase:
        print("🤖 Supabase is READY!")
    else:
        print("⚠️ Supabase credentials not found")
except ImportError:
    supabase = None
    print("⚠️ supabase not installed. Run: pip install supabase")

from app.utils.usda_api import usda_api
from app.utils.file_handler import save_uploaded_file
from app.models.ml_model import classifier
from app.utils.nutrition_data_v2 import (
    get_questions_for_food,
    calculate_nutrition,
    get_all_foods,
    validate_answers,
    FOOD_QUESTIONS
)

print("API FILE LOADED 🚀")

router = APIRouter()


# ============================================
# USER PROFILE FUNCTIONS
# ============================================

def calculate_daily_calorie_goal(height_cm: int, weight_kg: float, age: int, gender: str, activity_level: str, goal: str) -> int:
    """Calculate daily calorie goal using Mifflin-St Jeor Equation"""
    if gender == 'female':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5

    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    daily_need = bmr * activity_multipliers.get(activity_level, 1.55)

    if goal == 'lose':
        daily_goal = daily_need - 500
    elif goal == 'gain':
        daily_goal = daily_need + 500
    else:
        daily_goal = daily_need

    return max(1200, int(daily_goal))


def generate_personalized_tip(consumed: int, goal: int, user_goal: str, percentage: int) -> str:
    """Generate personalized tip based on progress"""
    remaining = goal - consumed
    over = consumed - goal if consumed > goal else 0

    if consumed >= goal:
        if user_goal == 'lose':
            return f"⚠️ You've exceeded your daily goal by {over} calories. Try lighter meals tomorrow or extra exercise."
        elif user_goal == 'gain':
            return f"🎉 You've reached your daily goal! {over} calories over. Great job, but don't overdo it."
        else:
            return f"📊 You've exceeded your daily goal by {over} calories. Balance the rest of the day with low-calorie choices."
    elif percentage < 25:
        if user_goal == 'lose':
            return f"🎯 Great start! You have {remaining} calories left. Focus on protein-rich foods to stay full."
        elif user_goal == 'gain':
            return f"💪 Time to eat! Only {percentage}% of your daily goal. Add a healthy shake or nuts."
        else:
            return f"🥗 Light eating so far. {remaining} calories remaining for balanced meals."
    elif percentage < 50:
        if user_goal == 'lose':
            return f"📊 On track! {remaining} calories left. Choose veggies and lean protein for dinner."
        elif user_goal == 'gain':
            return f"✅ Good progress! Add a calorie-dense snack like peanut butter or avocado."
        else:
            return f"👍 Balanced eating! Keep going with your remaining {remaining} calories."
    elif percentage < 75:
        if user_goal == 'lose':
            return f"⚠️ Watch your portions. You have {remaining} calories left. Consider a light dinner."
        elif user_goal == 'gain':
            return f"🍽️ Almost there! You need {remaining} more calories. A protein shake can help."
        else:
            return f"📌 You've had {percentage}% of your calories. Plan remaining meals wisely."
    else:
        if user_goal == 'lose':
            return f"🔴 Close to your limit! Only {remaining} calories left. Opt for tea or water."
        elif user_goal == 'gain':
            return f"💪 Almost at your goal! You need {remaining} more calories. Keep eating."
        else:
            return f"📊 Almost reached your daily goal. {remaining} calories remaining - choose wisely!"


# ============================================
# PROFILE ENDPOINTS
# ============================================

@router.post("/profile/save")
async def save_profile(
        token: str = Form(...),
        height_cm: int = Form(...),
        weight_kg: float = Form(...),
        age: int = Form(...),
        gender: str = Form(...),
        activity_level: str = Form(...),
        goal: str = Form(...)
):
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}
    try:
        user = supabase.auth.get_user(token)
        if not user:
            return {"success": False, "error": "Invalid token"}

        daily_calorie_goal = calculate_daily_calorie_goal(
            height_cm, weight_kg, age, gender, activity_level, goal
        )

        data = {
            "user_id": user.user.id,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "age": age,
            "gender": gender,
            "activity_level": activity_level,
            "goal": goal,
            "daily_calorie_goal": daily_calorie_goal,
            "updated_at": datetime.now().isoformat()
        }

        result = supabase.table("user_profiles").upsert(data).execute()

        return {
            "success": True,
            "profile": result.data[0] if result.data else None,
            "daily_calorie_goal": daily_calorie_goal,
            "message": "Profile saved successfully!"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/profile/get")
async def get_profile(token: str):
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}
    try:
        user = supabase.auth.get_user(token)
        if not user:
            return {"success": False, "error": "Invalid token"}

        result = supabase.table("user_profiles").select("*").eq("user_id", user.user.id).execute()
        if result.data:
            return {"success": True, "profile": result.data[0]}
        else:
            return {"success": True, "profile": None, "message": "No profile found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/profile/daily-progress")
async def get_daily_progress(token: str):
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}
    try:
        user = supabase.auth.get_user(token)
        if not user:
            return {"success": False, "error": "Invalid token"}

        profile_result = supabase.table("user_profiles").select("*").eq("user_id", user.user.id).execute()
        if not profile_result.data:
            return {"success": False, "error": "Please complete profile setup first"}

        profile = profile_result.data[0]
        daily_goal = profile['daily_calorie_goal']

        today = datetime.now().date().isoformat()
        meals_result = supabase.table("meals").select("nutrition", "created_at").eq("user_id", user.user.id).execute()

        total_calories = 0
        for meal in meals_result.data:
            created_date = datetime.fromisoformat(meal.get('created_at', '')).date().isoformat()
            if created_date == today:
                total_calories += meal.get('nutrition', {}).get('calories', 0)

        remaining = max(0, daily_goal - total_calories)
        percentage = min(100, int((total_calories / daily_goal) * 100)) if daily_goal > 0 else 0

        tip = generate_personalized_tip(total_calories, daily_goal, profile['goal'], percentage)

        return {
            "success": True,
            "daily_goal": daily_goal,
            "consumed": total_calories,
            "remaining": remaining,
            "percentage": percentage,
            "tip": tip,
            "goal_type": profile['goal']
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.put("/profile/update-weight")
async def update_weight(token: str = Form(...), new_weight: float = Form(...)):
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}
    try:
        user = supabase.auth.get_user(token)
        if not user:
            return {"success": False, "error": "Invalid token"}

        profile_result = supabase.table("user_profiles").select("*").eq("user_id", user.user.id).execute()
        if not profile_result.data:
            return {"success": False, "error": "No profile found"}

        profile = profile_result.data[0]
        new_daily_goal = calculate_daily_calorie_goal(
            profile['height_cm'], new_weight, profile['age'],
            profile['gender'], profile['activity_level'], profile['goal']
        )

        supabase.table("user_profiles").update({
            "weight_kg": new_weight,
            "daily_calorie_goal": new_daily_goal,
            "updated_at": datetime.now().isoformat()
        }).eq("user_id", user.user.id).execute()

        return {
            "success": True,
            "new_weight": new_weight,
            "new_daily_goal": new_daily_goal,
            "message": "Weight updated successfully!"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# FOOD ENDPOINTS
# ============================================

@router.get("/foods")
async def list_all_foods():
    try:
        foods = get_all_foods()
        return {
            "success": True,
            "total": len(foods),
            "foods": foods,
            "display_names": [f.replace('_', ' ').title() for f in foods]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/food/{food_name}/questions")
async def get_food_questions(food_name: str):
    try:
        result = get_questions_for_food(food_name, {})
        if result['success']:
            return {"success": True, "data": result}
        else:
            return {
                "success": False,
                "message": result.get('message', 'Food not found'),
                "fallback_questions": result.get('questions', []),
                "fallback_nutrition": result.get('base_nutrition', {})
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/questions/process")
async def process_questions_answers(
        food_name: str = Form(...),
        answers: str = Form("{}")
):
    """
    Process answers to questions and return nutrition estimate
    (No custom input handling – all answers are pre-defined options)
    """
    try:
        answers_dict = json.loads(answers)
        nutrition = calculate_nutrition(food_name, answers_dict)

        print(f"📊 Final nutrition: {nutrition['calories']} cal, {nutrition['sugar']}g sugar")

        return {
            "success": True,
            "nutrition": nutrition,
            "food": food_name,
            "food_display": food_name.replace('_', ' ').title(),
            "answers_provided": answers_dict,
            "questions_answered": len(answers_dict),
            "message": f"Estimated nutrition for {food_name.replace('_', ' ').title()}"
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid answers format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.get("/questions/preview/{food_name}")
async def preview_questions(food_name: str):
    try:
        result = get_questions_for_food(food_name, {})
        if result['success']:
            return {
                "success": True,
                "food": food_name,
                "food_display": food_name.replace('_', ' ').title(),
                "total_questions": result['total_questions'],
                "questions": result['questions'],
                "base_nutrition": result['base_nutrition']
            }
        else:
            return {
                "success": False,
                "food": food_name,
                "message": "Food not found in database, showing generic questions",
                "total_questions": len(result.get('questions', [])),
                "questions": result.get('questions', []),
                "base_nutrition": result.get('base_nutrition', {})
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete-flow")
async def complete_flow(
        file: UploadFile = File(None),
        food_name: str = Form(None),
        answers: str = Form("{}")
):
    print("=" * 50)
    print("🔥 COMPLETE FLOW HIT! 🔥")
    print("=" * 50)
    try:
        print(f"📥 Received request - file: {file.filename if file else 'None'}, food: {food_name}")

        answers_dict = json.loads(answers) if answers else {}
        result = {"success": True}
        detected_food = None

        if file:
            try:
                file_path = await save_uploaded_file(file)
                print(f"💾 File saved at: {file_path}")

                prediction = classifier.predict_category(file_path)
                print(f"🤖 Prediction: {prediction}")

                if prediction.get("is_unknown"):
                    print(f"⚠️ Unknown food detected with confidence {prediction.get('confidence', 0)}")
                    return {
                        "success": False,
                        "error": "❓ Could not identify the food in this image. Please try a clearer photo or select from our 7 supported foods: Pizza, Burger, Fried Rice, Ice Cream, Cheesecake, Samosa, French Fries.",
                        "supported_foods": ["Pizza", "Burger", "Fried Rice", "Ice Cream", "Cheesecake", "Samosa", "French Fries"],
                        "confidence": prediction.get("confidence", 0)
                    }

                detected_food = prediction.get("food", "pizza")
                display_name = prediction.get("display_name", detected_food.replace('_', ' ').title())
                emoji = prediction.get("emoji", "🍽️")
                confidence = prediction.get("confidence", 0.9)
                category = prediction.get("category", "flatbreads")

                result.update({
                    "detected_food": detected_food,
                    "display_name": display_name,
                    "emoji": emoji,
                    "category": category,
                    "detection_confidence": confidence,
                    "is_mock": prediction.get("is_mock", False),
                    "image_url": f"/uploads/{os.path.basename(file_path)}"
                })
                final_food = detected_food
                print(f"🍽️ Using food: {final_food} for questions")

            except Exception as e:
                print(f"❌ File processing error: {e}")
                import traceback
                traceback.print_exc()
                return {"success": False, "error": f"File processing failed: {str(e)}"}

        elif food_name:
            final_food = food_name
            detected_food = food_name
            result.update({"provided_food": final_food})
            print(f"🍽️ Using provided food: {final_food}")
        else:
            return {"success": False, "error": "Either file or food_name is required"}

        if not answers_dict:
            food_for_questions = detected_food if detected_food else final_food
            print(f"📋 Getting questions for: {food_for_questions}")

            questions_data = get_questions_for_food(food_for_questions, answers_dict)
            print(f"📋 Questions data: {questions_data.get('total_questions')} questions found")

            if questions_data['success']:
                result.update({
                    "stage": "questions",
                    "food": food_for_questions,
                    "food_display": food_for_questions.replace('_', ' ').title(),
                    "questions": questions_data['questions'],
                    "base_nutrition": questions_data['base_nutrition'],
                    "total_questions": questions_data['total_questions'],
                    "detection_confidence": prediction.get("confidence", 0.9) if file else 1.0,
                    "training_status": prediction.get("training_status", "unknown") if file else "direct"
                })
                print(f"✅ Using questions for: {food_for_questions}")
            else:
                print(f"⚠️ No questions found for {food_for_questions}, using defaults")
                result.update({
                    "stage": "questions",
                    "food": food_for_questions,
                    "food_display": food_for_questions.replace('_', ' ').title(),
                    "questions": [{
                        "id": "0",
                        "text": f"How many servings of {food_for_questions.replace('_', ' ').title()} did you have?",
                        "type": "single_select",
                        "options": [
                            {"value": "1", "label": "1 serving"},
                            {"value": "2", "label": "2 servings"},
                            {"value": "3", "label": "3 servings"},
                            {"value": "4", "label": "4 servings"}
                        ]
                    }],
                    "base_nutrition": {
                        "calories": 200,
                        "protein": 5,
                        "carbs": 20,
                        "fat": 10,
                        "fiber": 1,
                        "sugar": 5
                    },
                    "total_questions": 1
                })
        else:
            nutrition = calculate_nutrition(final_food, answers_dict)
            print(f"🍽️ Nutrition calculated for {final_food}")
            result.update({
                "stage": "nutrition",
                "food": final_food,
                "food_display": final_food.replace('_', ' ').title(),
                "nutrition": nutrition,
                "answers_provided": answers_dict,
                "questions_answered": len(answers_dict)
            })

        return result

    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid answers format"}
    except Exception as e:
        import traceback
        print("🔥 COMPLETE FLOW ERROR:")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


# ============================================
# SUPABASE AUTHENTICATION & MEAL HISTORY
# ============================================

@router.post("/auth/signup")
async def signup(email: str = Form(...), password: str = Form(...)):
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}
    try:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"success": False, "error": "Invalid email format"}
        if len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}

        result = supabase.auth.sign_up({"email": email, "password": password})
        return {
            "success": True,
            "user": {"id": result.user.id, "email": result.user.email},
            "message": "User created successfully! Please check your email to verify."
        }
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return {"success": False, "error": "Email already registered"}
        return {"success": False, "error": error_msg}


@router.post("/auth/login")
async def login(email: str = Form(...), password: str = Form(...)):
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}
    try:
        result = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return {
            "success": True,
            "access_token": result.session.access_token,
            "refresh_token": result.session.refresh_token,
            "user": {"id": result.user.id, "email": result.user.email},
            "message": "Login successful!"
        }
    except Exception as e:
        return {"success": False, "error": "Invalid email or password"}


@router.post("/auth/logout")
async def logout(token: str = Form(...)):
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}
    try:
        supabase.auth.sign_out()
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/auth/me")
async def get_current_user(token: str):
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}
    try:
        user = supabase.auth.get_user(token)
        return {"success": True, "user": {"id": user.user.id, "email": user.user.email}}
    except Exception as e:
        return {"success": False, "error": "Invalid or expired token"}


@router.post("/meals/save")
async def save_meal(
        token: str = Form(...),
        food_name: str = Form(...),
        calories: int = Form(...),
        protein: float = Form(...),
        carbs: float = Form(...),
        fat: float = Form(...),
        sugar: float = Form(...),
        answers: str = Form("{}")
):
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}
    try:
        user = supabase.auth.get_user(token)
        if not user:
            return {"success": False, "error": "Invalid token"}

        nutrition = {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "sugar": sugar
        }
        data = {
            "user_id": user.user.id,
            "food_name": food_name,
            "nutrition": nutrition,
            "answers": json.loads(answers) if answers else {},
            "created_at": datetime.now().isoformat()
        }
        result = supabase.table("meals").insert(data).execute()
        return {"success": True, "meal": result.data[0] if result.data else None}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/meals/history")
async def get_meal_history(token: str, limit: int = 20):
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}
    try:
        user = supabase.auth.get_user(token)
        if not user:
            return {"success": False, "error": "Invalid token"}
        result = supabase.table("meals").select("*").eq("user_id", user.user.id).order("created_at", desc=True).limit(limit).execute()
        return {"success": True, "meals": result.data}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.delete("/meals/delete/{meal_id}")
async def delete_meal(meal_id: int, token: str):
    if not supabase:
        return {"success": False, "error": "Supabase not configured"}
    try:
        user = supabase.auth.get_user(token)
        if not user:
            return {"success": False, "error": "Invalid token"}
        meal = supabase.table("meals").select("*").eq("id", meal_id).eq("user_id", user.user.id).execute()
        if not meal.data:
            return {"success": False, "error": "Meal not found"}
        supabase.table("meals").delete().eq("id", meal_id).execute()
        return {"success": True, "message": "Meal deleted successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# USDA API ENDPOINTS
# ============================================

@router.get("/usda-search")
async def search_usda_food(query: str):
    try:
        results = usda_api.search_food(query)
        if results:
            foods = []
            for food in results[:5]:
                foods.append({
                    'name': food.get('description', 'Unknown'),
                    'fdc_id': food.get('fdcId'),
                    'brand': food.get('brandName', 'Generic'),
                })
            return {"success": True, "query": query, "results": foods, "count": len(foods)}
        return {"success": False, "message": f"No foods found for '{query}'"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/usda-nutrients")
async def get_usda_nutrients(query: str):
    try:
        data = usda_api.get_nutrients_by_name(query)
        if data:
            return {"success": True, "food_name": data['food_name'], "nutrients": data['nutrients']}
        return {"success": False, "message": f"No data found for '{query}'"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/usda-nutrients/{fdc_id}")
async def get_usda_nutrients_by_id(fdc_id: int):
    try:
        data = usda_api.get_food_nutrients(fdc_id)
        if data:
            nutrients = []
            for nutrient in data.get('foodNutrients', [])[:20]:
                nutrients.append({
                    'name': nutrient.get('nutrient', {}).get('name'),
                    'amount': nutrient.get('amount'),
                    'unit': nutrient.get('nutrient', {}).get('unitName')
                })
            return {"success": True, "food_name": data.get('description'), "nutrients": nutrients}
        return {"success": False, "message": f"No data found for FDC ID {fdc_id}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# HEALTH CHECK
# ============================================

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_available": False,
        "supabase_available": supabase is not None,
        "service": "NutriValue API"
    }