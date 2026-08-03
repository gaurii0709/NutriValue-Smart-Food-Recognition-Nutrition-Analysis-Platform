from .nutrition_data_v2 import FOOD_QUESTIONS

FOOD_NUTRITION = FOOD_QUESTIONS


# ------------------ GET QUESTIONS ------------------

def get_questions_for_food(food_name):
    food_name = food_name.lower()

    if food_name in FOOD_NUTRITION:
        food_data = FOOD_NUTRITION[food_name]

        return {
            'success': True,
            'food': food_name,
            'questions': food_data['questions'],
            'base_nutrition': food_data.get('base_nutrition') or food_data.get('base_calories')
        }

    # fallback
    return {
        'success': False,
        'food': food_name,
        'questions': [],
        'base': {
            'calories': 200,
            'protein': 5,
            'carbs': 20,
            'fat': 10
        }
    }


# ------------------ CALCULATION ENGINE ------------------

def calculate_nutrition(food_name, answers):
    food_name = food_name.lower()

    if food_name not in FOOD_NUTRITION:
        return _default_response(food_name)

    food_data = FOOD_NUTRITION[food_name]

    # ------------------ BASE ------------------

    base_data = food_data.get('base_nutrition') or food_data.get('base_calories')

    total = {
        'calories': 0,
        'protein': 0,
        'fat': 0,
        'carbs': 0
    }

    selected_base = None

    # ------------------ FIRST PASS (GET BASE) ------------------

    for question in food_data['questions']:
        qid = question['id']

        if qid not in answers:
            continue

        answer = answers[qid]

        # handle single_select
        if question['type'] == 'single_select':
            for option in question.get('options', []):
                if option['value'] == answer:
                    if 'base_key' in option:
                        selected_base = option['base_key']

        # handle multi_select
        elif question['type'] == 'multi_select':
            if not isinstance(answer, list):
                continue
            for selected in answer:
                for option in question.get('options', []):
                    if option['value'] == selected:
                        if 'base_key' in option:
                            selected_base = option['base_key']

    # ------------------ APPLY BASE ------------------

    if isinstance(base_data, dict):

        # CASE 1: base_nutrition with sizes
        if selected_base and selected_base in base_data:
            total.update(base_data[selected_base])

        # CASE 2: base_nutrition default
        elif 'calories' in base_data:
            total.update(base_data)

        # CASE 3: base_calories
        else:
            first_value = list(base_data.values())[0]
            total['calories'] = first_value
            total['protein'] = round(first_value * 0.05, 1)
            total['fat'] = round(first_value * 0.04, 1)
            total['carbs'] = round(first_value * 0.12, 1)

    # ------------------ SECOND PASS (MODIFIERS) ------------------

    final_multiplier = 1.0

    for question in food_data['questions']:
        qid = question['id']

        if qid not in answers:
            continue

        answer = answers[qid]

        # -------- SINGLE SELECT --------
        if question['type'] == 'single_select':
            for option in question.get('options', []):
                if option['value'] == answer:

                    # nutrition addition
                    if 'nutrition' in option:
                        _add_nutrition(total, option['nutrition'])

                    # old calorie_modifier support
                    if 'calorie_modifier' in option:
                        total['calories'] += option['calorie_modifier']

                    # multipliers
                    if 'calorie_multiplier' in option:
                        final_multiplier *= option['calorie_multiplier']

                    if 'portion_multiplier' in option:
                        final_multiplier *= option['portion_multiplier']

                    if 'final_multiplier' in option:
                        final_multiplier *= option['final_multiplier']

        # -------- MULTI SELECT --------
        elif question['type'] == 'multi_select':

            if not isinstance(answer, list):
                continue

            # 🚨 handle "none"
            if 'none' in answer:
                continue

            for selected in answer:
                for option in question.get('options', []):
                    if option['value'] == selected:

                        if 'nutrition' in option:
                            _add_nutrition(total, option['nutrition'])

                        if 'calorie_modifier' in option:
                            total['calories'] += option['calorie_modifier']

    # ------------------ APPLY FINAL MULTIPLIER ------------------

    for key in total:
        total[key] = round(total[key] * final_multiplier, 1)

    # ------------------ FINAL RESPONSE ------------------

    return {
        **total,
        'food_display': food_data.get('name', food_name.title()),
        'emoji': food_data.get('emoji', '🍽️')
    }


# ------------------ HELPERS ------------------

def _add_nutrition(total, addition):
    for key in ['calories', 'protein', 'fat', 'carbs']:
        if key in addition:
            total[key] += addition[key]


def _default_response(food_name):
    return {
        'calories': 200,
        'protein': 5,
        'carbs': 20,
        'fat': 10,
        'food_display': food_name.replace('_', ' ').title(),
        'emoji': '🍽️'
    }