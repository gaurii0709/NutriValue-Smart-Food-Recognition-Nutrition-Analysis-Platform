# nutrition_data_v2.py — Clean, no "Other", no ambiguous wording, full rules

FOOD_ALIASES = {
    'hamburger': 'burger',
    'fries': 'french_fries',
    'frenchfries': 'french_fries',
    'icecream': 'ice_cream',
    'friedrice': 'fried_rice',
}

FOOD_QUESTIONS = {
    'pizza': {
        'name': 'Pizza',
        'emoji': '🍕',
        'base_nutrition': {'calories': 250, 'protein': 11, 'fat': 10, 'carbs': 30, 'sugar': 3},
        'questions': [
            {'id': 'q1_type', 'text': 'Veg or Non‑Veg?', 'type': 'single_select',
             'options': [{'value': 'veg', 'label': 'Vegetarian'}, {'value': 'non_veg', 'label': 'Non‑Vegetarian'}]},
            {'id': 'q2_size', 'text': 'Pizza size?', 'type': 'single_select',
             'options': [
                 {'value': 'small', 'label': 'Small (6 inch)', 'multiplier': 0.8},
                 {'value': 'medium', 'label': 'Medium (9-10 inch)', 'multiplier': 1.0},
                 {'value': 'large', 'label': 'Large (12 inch)', 'multiplier': 1.3},
                 {'value': 'extra_large', 'label': 'Extra Large (14 inch)', 'multiplier': 1.6}]},
            {'id': 'q3_crust', 'text': 'Crust type?', 'type': 'single_select',
             'options': [
                 {'value': 'thin', 'label': 'Thin crust', 'nutrition': {'calories': -30, 'carbs': -4}},
                 {'value': 'regular', 'label': 'Regular crust'},
                 {'value': 'pan', 'label': 'Pan / thick crust', 'nutrition': {'calories': 60, 'carbs': 8}},
                 {'value': 'stuffed', 'label': 'Stuffed crust', 'nutrition': {'calories': 120, 'carbs': 10, 'sugar': 1}}]},
            {'id': 'q4_veg_toppings', 'text': 'Choose veg toppings', 'type': 'multi_select',
             'condition': {'q1_type': 'veg'},
             'options': [
                 {'value': 'mushroom', 'label': 'Mushroom', 'nutrition': {'calories': 15, 'protein': 1, 'carbs': 2}},
                 {'value': 'capsicum_onion', 'label': 'Capsicum & Onion', 'nutrition': {'calories': 20, 'carbs': 4, 'sugar': 2}},
                 {'value': 'paneer', 'label': 'Paneer', 'nutrition': {'calories': 70, 'protein': 4, 'fat': 5, 'carbs': 2}},
                 {'value': 'mixed_veg', 'label': 'Mixed veggies', 'nutrition': {'calories': 30, 'carbs': 5, 'sugar': 2}}]},
            {'id': 'q5_nonveg_toppings', 'text': 'Choose meat toppings', 'type': 'multi_select',
             'condition': {'q1_type': 'non_veg'},
             'options': [
                 {'value': 'chicken', 'label': 'Chicken', 'nutrition': {'calories': 60, 'protein': 5, 'fat': 3}},
                 {'value': 'pepperoni', 'label': 'Pepperoni', 'nutrition': {'calories': 90, 'protein': 4, 'fat': 8, 'carbs': 1}},
                 {'value': 'bacon', 'label': 'Bacon', 'nutrition': {'calories': 100, 'protein': 4, 'fat': 9, 'carbs': 1}},
                 {'value': 'mixed_meat', 'label': 'Mixed meat', 'nutrition': {'calories': 120, 'protein': 7, 'fat': 10, 'carbs': 1}}]},
            {'id': 'q6_chicken_style', 'text': 'How is the chicken prepared?', 'type': 'single_select',
             'condition': {'q5_nonveg_toppings': 'chicken'},
             'options': [
                 {'value': 'grilled', 'label': 'Grilled'},
                 {'value': 'fried', 'label': 'Fried / crispy', 'nutrition': {'calories': 60, 'fat': 5, 'carbs': 2}},
                 {'value': 'tandoori', 'label': 'Tandoori', 'nutrition': {'calories': 30, 'fat': 2, 'carbs': 1}},
                 {'value': 'butter_chicken', 'label': 'Butter chicken', 'nutrition': {'calories': 90, 'fat': 7, 'carbs': 3, 'sugar': 2}}]},
            {'id': 'q7_cheese', 'text': 'Extra cheese?', 'type': 'single_select',
             'options': [
                 {'value': 'no', 'label': 'No'},
                 {'value': 'normal', 'label': 'Yes (normal)', 'nutrition': {'calories': 70, 'protein': 4, 'fat': 6, 'carbs': 1}},
                 {'value': 'extra', 'label': 'Yes (extra)', 'nutrition': {'calories': 130, 'protein': 7, 'fat': 11, 'carbs': 2}}]},
            {'id': 'q8_slices', 'text': 'How many slices did you eat?', 'type': 'single_select',
             'options': [
                 {'value': '1', 'label': '1 slice', 'multiplier': 1},
                 {'value': '2', 'label': '2 slices', 'multiplier': 2},
                 {'value': '3', 'label': '3 slices', 'multiplier': 3},
                 {'value': '4', 'label': '4 slices', 'multiplier': 4},
                 {'value': '5', 'label': '5 slices', 'multiplier': 5},
                 {'value': '6', 'label': '6 slices', 'multiplier': 6},
                 {'value': '7', 'label': '7 slices', 'multiplier': 7},
                 {'value': '8', 'label': '8 slices (whole pizza)', 'multiplier': 8}]}
        ]
    },
    'burger': {
        'name': 'Burger',
        'emoji': '🍔',
        'base_nutrition': {'calories': 250, 'protein': 12, 'fat': 10, 'carbs': 25, 'sugar': 5},
        'questions': [
            {'id': 'q1_type', 'text': 'Veg or Non‑Veg?', 'type': 'single_select',
             'options': [{'value': 'veg', 'label': 'Vegetarian'}, {'value': 'non_veg', 'label': 'Non‑Vegetarian'}]},
            {'id': 'q2_patty', 'text': 'Main patty?', 'type': 'single_select',
             'options': [
                 {'value': 'aloo', 'label': 'Aloo (Potato)', 'condition': {'q1_type': 'veg'}, 'nutrition': {'calories': 30, 'protein': 1, 'fat': 1, 'carbs': 5}},
                 {'value': 'paneer', 'label': 'Paneer', 'condition': {'q1_type': 'veg'}, 'nutrition': {'calories': 80, 'protein': 5, 'fat': 6, 'carbs': 2}},
                 {'value': 'mixed_veg', 'label': 'Mixed Veg', 'condition': {'q1_type': 'veg'}, 'nutrition': {'calories': 40, 'protein': 1, 'fat': 1, 'carbs': 6, 'sugar': 2}},
                 {'value': 'chicken', 'label': 'Chicken', 'condition': {'q1_type': 'non_veg'}, 'nutrition': {'calories': 90, 'protein': 8, 'fat': 5}},
                 {'value': 'mutton', 'label': 'Mutton', 'condition': {'q1_type': 'non_veg'}, 'nutrition': {'calories': 140, 'protein': 9, 'fat': 11}},
                 {'value': 'fish', 'label': 'Fish', 'condition': {'q1_type': 'non_veg'}, 'nutrition': {'calories': 80, 'protein': 7, 'fat': 5}}]},
            {'id': 'q3_sauces', 'text': 'Sauces?', 'type': 'multi_select',
             'options': [
                 {'value': 'mayo', 'label': 'Mayo', 'nutrition': {'calories': 90, 'fat': 10}},
                 {'value': 'ketchup', 'label': 'Ketchup', 'nutrition': {'calories': 30, 'carbs': 8, 'sugar': 7}},
                 {'value': 'schezwan', 'label': 'Schezwan', 'nutrition': {'calories': 70, 'fat': 5, 'carbs': 6, 'sugar': 2}},
                 {'value': 'mustard', 'label': 'Mustard', 'nutrition': {'calories': 20}}]},
            {'id': 'q4_addons', 'text': 'Extra add‑ons?', 'type': 'multi_select',
             'options': [
                 {'value': 'veggies', 'label': 'Extra veggies', 'nutrition': {'calories': 15}},
                 {'value': 'onion_rings', 'label': 'Onion rings', 'nutrition': {'calories': 70, 'fat': 4, 'carbs': 8, 'sugar': 2}},
                 {'value': 'grilled_mushroom', 'label': 'Grilled mushrooms', 'condition': {'q1_type': 'veg'}, 'nutrition': {'calories': 35, 'protein': 2}},
                 {'value': 'egg', 'label': 'Egg', 'condition': {'q1_type': 'non_veg'}, 'nutrition': {'calories': 70, 'protein': 6, 'fat': 5}},
                 {'value': 'bacon', 'label': 'Bacon', 'condition': {'q1_type': 'non_veg'}, 'nutrition': {'calories': 110, 'protein': 5, 'fat': 9}}]},
            {'id': 'q5_size', 'text': 'Number of patties?', 'type': 'single_select',
             'options': [
                 {'value': 'single', 'label': 'Single', 'multiplier': 1.0},
                 {'value': 'double', 'label': 'Double', 'multiplier': 1.8},
                 {'value': 'triple', 'label': 'Triple', 'multiplier': 2.5}]}
        ]
    },
    'fried_rice': {
        'name': 'Fried Rice',
        'emoji': '🍚',
        'base_nutrition': {'calories': 350, 'protein': 8, 'fat': 10, 'carbs': 50, 'sugar': 2},
        'questions': [
            {'id': 'q1_type', 'text': 'Veg or Non‑Veg?', 'type': 'single_select',
             'options': [{'value': 'veg', 'label': 'Veg'}, {'value': 'non_veg', 'label': 'Non‑Veg'}]},
            {'id': 'q2_additions', 'text': 'What does it include?', 'type': 'multi_select',
             'options': [
                 {'value': 'veg_mix', 'label': 'Mixed vegetables', 'condition': {'q1_type': 'veg'}, 'nutrition': {'calories': 30, 'carbs': 6, 'sugar': 2}},
                 {'value': 'paneer', 'label': 'Paneer', 'condition': {'q1_type': 'veg'}, 'nutrition': {'calories': 90, 'protein': 5, 'fat': 7, 'carbs': 2}},
                 {'value': 'egg', 'label': 'Egg', 'condition': {'q1_type': 'non_veg'}, 'nutrition': {'calories': 70, 'protein': 6, 'fat': 5}},
                 {'value': 'chicken', 'label': 'Chicken', 'condition': {'q1_type': 'non_veg'}, 'nutrition': {'calories': 90, 'protein': 8, 'fat': 6}},
                 {'value': 'extra_sauce', 'label': 'Extra sauces', 'nutrition': {'calories': 60, 'fat': 4, 'carbs': 6, 'sugar': 3}}]},
            {'id': 'q3_portion', 'text': 'Portion size?', 'type': 'single_select',
             'options': [
                 {'value': 'half', 'label': 'Half bowl (≈250g)', 'portion_multiplier': 0.6},
                 {'value': 'full', 'label': 'Full bowl (≈400g)', 'portion_multiplier': 1.0},
                 {'value': 'large', 'label': 'Large bowl (≈600g)', 'portion_multiplier': 1.4}]},
            {'id': 'q4_oil', 'text': 'Oil level?', 'type': 'single_select',
             'options': [
                 {'value': 'low', 'label': 'Low oil', 'nutrition': {'calories': -50, 'fat': -5}},
                 {'value': 'normal', 'label': 'Normal'},
                 {'value': 'oily', 'label': 'Oily', 'nutrition': {'calories': 120, 'fat': 12}}]},
            {'id': 'q5_style', 'text': 'Cooking style?', 'type': 'single_select',
             'options': [
                 {'value': 'homemade', 'label': 'Homemade', 'nutrition': {'calories': -80, 'fat': -8, 'carbs': -5}},
                 {'value': 'restaurant', 'label': 'Restaurant', 'nutrition': {'calories': 180, 'fat': 18, 'carbs': 12, 'sugar': 2}},
                 {'value': 'street', 'label': 'Street food', 'nutrition': {'calories': 280, 'fat': 28, 'carbs': 18, 'sugar': 3}}]}
        ]
    },
    'ice_cream': {
        'name': 'Ice Cream',
        'emoji': '🍦',
        'base_nutrition': {'calories': 180, 'protein': 3, 'fat': 10, 'carbs': 22, 'sugar': 21},
        'questions': [
            {'id': 'q1_type', 'text': 'Type?', 'type': 'single_select',
             'options': [{'value': 'cone', 'label': 'Cone'}, {'value': 'cup', 'label': 'Cup'},
                         {'value': 'stick', 'label': 'Stick / bar'}, {'value': 'sundae', 'label': 'Sundae'}]},
            {'id': 'q2_flavor', 'text': 'Flavor?', 'type': 'single_select',
             'options': [
                 {'value': 'vanilla', 'label': 'Vanilla'},
                 {'value': 'chocolate', 'label': 'Chocolate', 'nutrition': {'calories': 25, 'carbs': 4, 'sugar': 3}},
                 {'value': 'butterscotch', 'label': 'Butterscotch', 'nutrition': {'calories': 35, 'carbs': 5, 'sugar': 4}},
                 {'value': 'fruit', 'label': 'Fruit‑based', 'nutrition': {'calories': 15, 'carbs': 4, 'sugar': 3}}]},
            {'id': 'q3_scoops', 'text': 'Scoops?', 'type': 'single_select',
             'options': [{'value': '1', 'label': '1 scoop', 'multiplier': 1},
                         {'value': '2', 'label': '2 scoops', 'multiplier': 2},
                         {'value': '3', 'label': '3 scoops', 'multiplier': 3}]},
            {'id': 'q4_density', 'text': 'Base type?', 'type': 'single_select',
             'options': [
                 {'value': 'regular', 'label': 'Regular'},
                 {'value': 'gelato', 'label': 'Gelato', 'nutrition': {'calories': 30, 'fat': 2, 'carbs': 3, 'sugar': 2}},
                 {'value': 'premium', 'label': 'Premium (rich)', 'nutrition': {'calories': 60, 'fat': 5, 'carbs': 4, 'sugar': 3}}]},
            {'id': 'q5_toppings', 'text': 'Toppings?', 'type': 'multi_select',
             'options': [
                 {'value': 'choco_syrup', 'label': 'Chocolate syrup', 'nutrition': {'calories': 60, 'fat': 3, 'carbs': 9, 'sugar': 8}},
                 {'value': 'caramel', 'label': 'Caramel syrup', 'nutrition': {'calories': 70, 'fat': 4, 'carbs': 10, 'sugar': 9}},
                 {'value': 'nuts', 'label': 'Nuts', 'nutrition': {'calories': 70, 'protein': 2, 'fat': 6, 'carbs': 2}},
                 {'value': 'sprinkles', 'label': 'Sprinkles', 'nutrition': {'calories': 40, 'fat': 2, 'carbs': 5, 'sugar': 4}}]},
            {'id': 'q6_cone', 'text': 'Cone type?', 'type': 'single_select', 'condition': {'q1_type': 'cone'},
             'options': [
                 {'value': 'regular', 'label': 'Regular cone', 'nutrition': {'calories': 50, 'carbs': 10, 'sugar': 1}},
                 {'value': 'waffle', 'label': 'Waffle cone', 'nutrition': {'calories': 80, 'fat': 3, 'carbs': 12, 'sugar': 2}},
                 {'value': 'choco_dip', 'label': 'Chocolate coated', 'nutrition': {'calories': 100, 'fat': 5, 'carbs': 12, 'sugar': 3}}]}
        ]
    },
    'cheesecake': {
        'name': 'Cheesecake',
        'emoji': '🍰',
        'base_nutrition': {'calories': 350, 'protein': 6, 'fat': 24, 'carbs': 28, 'sugar': 18},
        'questions': [
            {'id': 'q1_slices', 'text': 'Number of slices?', 'type': 'number_input', 'min': 1, 'max': 6, 'multiplier_per_unit': True},
            {'id': 'q2_type', 'text': 'Type?', 'type': 'single_select',
             'options': [
                 {'value': 'baked', 'label': 'Baked', 'nutrition': {'calories': 40, 'fat': 4, 'carbs': 3, 'sugar': 2}},
                 {'value': 'no_bake', 'label': 'No‑bake'},
                 {'value': 'basque', 'label': 'Basque', 'nutrition': {'calories': 100, 'fat': 8, 'carbs': 5, 'sugar': 3}}]},
            {'id': 'q3_toppings', 'text': 'Toppings?', 'type': 'multi_select',
             'options': [
                 {'value': 'fruit_topping', 'label': 'Fruit topping', 'nutrition': {'calories': 50, 'carbs': 12, 'sugar': 10}},
                 {'value': 'choco_syrup', 'label': 'Chocolate syrup', 'nutrition': {'calories': 60, 'fat': 3, 'carbs': 9, 'sugar': 8}},
                 {'value': 'whipped_cream', 'label': 'Whipped cream', 'nutrition': {'calories': 60, 'fat': 6, 'carbs': 2, 'sugar': 1}}]}
        ]
    },
    'samosa': {
        'name': 'Samosa',
        'emoji': '🥟',
        'base_nutrition': {'calories': 160, 'protein': 3, 'fat': 9, 'carbs': 18, 'sugar': 1},
        'questions': [
            {'id': 'q1_type', 'text': 'Type?', 'type': 'single_select',
             'options': [
                 {'value': 'aloo', 'label': 'Aloo (Potato)'},
                 {'value': 'paneer', 'label': 'Paneer', 'nutrition': {'calories': 60, 'protein': 3, 'fat': 4, 'carbs': 2}},
                 {'value': 'non_veg', 'label': 'Non‑veg', 'nutrition': {'calories': 80, 'protein': 5, 'fat': 6, 'carbs': 1}}]},
            {'id': 'q2_quantity', 'text': 'How many?', 'type': 'number_input', 'min': 1, 'max': 10, 'multiplier_per_unit': True},
            {'id': 'q3_size', 'text': 'Size?', 'type': 'single_select',
             'options': [
                 {'value': 'small', 'label': 'Small', 'portion_multiplier': 0.8},
                 {'value': 'medium', 'label': 'Medium', 'portion_multiplier': 1.0},
                 {'value': 'large', 'label': 'Large', 'portion_multiplier': 1.3}]},
            {'id': 'q4_oil', 'text': 'Oil level?', 'type': 'single_select',
             'options': [
                 {'value': 'low', 'label': 'Low (baked/air‑fried)', 'nutrition': {'calories': -30, 'fat': -3}},
                 {'value': 'normal', 'label': 'Normal (deep fried)'},
                 {'value': 'oily', 'label': 'Oily (street food)', 'nutrition': {'calories': 60, 'fat': 6}}]},
            {'id': 'q5_sides', 'text': 'Chutney or sides?', 'type': 'multi_select',
             'options': [
                 {'value': 'green_chutney', 'label': 'Green chutney', 'nutrition': {'calories': 20, 'fat': 1, 'carbs': 3, 'sugar': 1}},
                 {'value': 'sweet_chutney', 'label': 'Sweet chutney', 'nutrition': {'calories': 40, 'carbs': 10, 'sugar': 8}},
                 {'value': 'ketchup', 'label': 'Ketchup', 'nutrition': {'calories': 30, 'carbs': 8, 'sugar': 7}},
                 {'value': 'fried_chillies', 'label': 'Fried green chillies', 'nutrition': {'calories': 30, 'fat': 2, 'carbs': 3}},
                 {'value': 'none', 'label': 'None'}]}
        ]
    },
    'french_fries': {
        'name': 'French Fries',
        'emoji': '🍟',
        'base_nutrition': {'calories': 320, 'protein': 4, 'fat': 15, 'carbs': 40, 'sugar': 0},
        'questions': [
            {'id': 'q1_size', 'text': 'Portion size?', 'type': 'single_select',
             'options': [
                 {'value': 'small', 'label': 'Small', 'multiplier': 0.7},
                 {'value': 'medium', 'label': 'Medium', 'multiplier': 1.0},
                 {'value': 'large', 'label': 'Large', 'multiplier': 1.4},
                 {'value': 'extra_large', 'label': 'Extra large', 'multiplier': 1.8}]},
            {'id': 'q2_type', 'text': 'Type?', 'type': 'single_select',
             'options': [{'value': 'plain', 'label': 'Plain'}, {'value': 'loaded', 'label': 'Loaded'},
                         {'value': 'cheesy', 'label': 'Cheesy', 'nutrition': {'calories': 120, 'fat': 10, 'protein': 5}}]},
            {'id': 'q3_plain_fry', 'text': 'How were they fried?', 'type': 'single_select', 'condition': {'q2_type': 'plain'},
             'options': [
                 {'value': 'light', 'label': 'Light (air fryer)', 'nutrition': {'calories': -50, 'fat': -5}},
                 {'value': 'normal', 'label': 'Normal (deep fried)'},
                 {'value': 'crispy', 'label': 'Extra crispy', 'nutrition': {'calories': 80, 'fat': 8}}]},
            {'id': 'q4_seasoning', 'text': 'Peri‑Peri masala?', 'type': 'single_select',
             'options': [
                 {'value': 'no', 'label': 'No'},
                 {'value': 'yes', 'label': 'Yes', 'nutrition': {'calories': 20, 'fat': 1}}]},
            {'id': 'q5_loaded_toppings', 'text': 'Toppings (for loaded/cheesy)', 'type': 'multi_select',
             'condition': {'q2_type': 'loaded'},
             'options': [
                 {'value': 'cheese_sauce', 'label': 'Cheese sauce', 'nutrition': {'calories': 120, 'fat': 10, 'protein': 5}},
                 {'value': 'mayo', 'label': 'Mayo', 'nutrition': {'calories': 140, 'fat': 15}},
                 {'value': 'jalapenos', 'label': 'Jalapenos', 'nutrition': {'calories': 20}},
                 {'value': 'bacon', 'label': 'Bacon bits', 'nutrition': {'calories': 100, 'protein': 6, 'fat': 8}}]}
        ]
    }
}

# =========================================================
# HELPER FUNCTIONS (with full apply_rules restored)
# =========================================================

def get_questions_for_food(food_name, answers=None):
    food_name = food_name.lower()
    if food_name in FOOD_ALIASES:
        food_name = FOOD_ALIASES[food_name]
    if food_name not in FOOD_QUESTIONS:
        return {
            'success': False,
            'message': f"Food '{food_name}' not found",
            'questions': [],
            'base_nutrition': {'calories': 200, 'protein': 5, 'fat': 10, 'carbs': 20, 'sugar': 5},
            'total_questions': 0
        }
    food_data = FOOD_QUESTIONS[food_name]
    questions = food_data['questions']
    if answers:
        questions = filter_questions(questions, answers)
    return {
        'success': True,
        'food': food_name,
        'food_display': food_data['name'],
        'emoji': food_data['emoji'],
        'questions': questions,
        'base_nutrition': food_data['base_nutrition'],
        'total_questions': len(questions)
    }

def filter_questions(questions, answers):
    if not answers:
        return questions
    filtered = []
    for q in questions:
        if 'condition' not in q:
            filtered.append(q)
            continue
        condition_met = True
        for key, value in q['condition'].items():
            user_val = answers.get(key)
            if isinstance(value, list):
                if user_val not in value:
                    condition_met = False
                    break
            else:
                if user_val != value:
                    condition_met = False
                    break
        if condition_met:
            filtered.append(q)
    return filtered

def calculate_nutrition(food_name, answers):
    food_name = food_name.lower()
    if food_name in FOOD_ALIASES:
        food_name = FOOD_ALIASES[food_name]
    if food_name not in FOOD_QUESTIONS:
        return default_response(food_name)

    food_data = FOOD_QUESTIONS[food_name]
    base = food_data['base_nutrition']

    calories = base['calories']
    protein = base['protein']
    fat = base['fat']
    carbs = base['carbs']
    sugar = base.get('sugar', 0)

    quantity_multiplier = 1.0
    portion_multiplier = 1.0
    final_multiplier = 1.0
    additions = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0, 'sugar': 0}

    for qid, answer in answers.items():
        for question in food_data['questions']:
            if question['id'] != qid:
                continue
            for option in question.get('options', []):
                if isinstance(answer, list):
                    match = option['value'] in answer
                else:
                    match = option['value'] == answer
                if not match:
                    continue
                if 'nutrition' in option:
                    additions['calories'] += option['nutrition'].get('calories', 0)
                    additions['protein'] += option['nutrition'].get('protein', 0)
                    additions['fat'] += option['nutrition'].get('fat', 0)
                    additions['carbs'] += option['nutrition'].get('carbs', 0)
                    additions['sugar'] += option['nutrition'].get('sugar', 0)
                if 'multiplier' in option:
                    quantity_multiplier *= option['multiplier']
                if 'portion_multiplier' in option:
                    portion_multiplier *= option['portion_multiplier']
                if 'final_multiplier' in option:
                    final_multiplier *= option['final_multiplier']

    for qid, answer in answers.items():
        if isinstance(answer, (int, float)) and not isinstance(answer, bool):
            for question in food_data['questions']:
                if question['id'] == qid and question.get('multiplier_per_unit'):
                    quantity_multiplier *= float(answer)

    calories = calories * quantity_multiplier
    protein = protein * quantity_multiplier
    fat = fat * quantity_multiplier
    carbs = carbs * quantity_multiplier
    sugar = sugar * quantity_multiplier

    calories += additions['calories']
    protein += additions['protein']
    fat += additions['fat']
    carbs += additions['carbs']
    sugar += additions['sugar']

    calories *= portion_multiplier
    protein *= portion_multiplier
    fat *= portion_multiplier
    carbs *= portion_multiplier
    sugar *= portion_multiplier

    calories *= final_multiplier
    protein *= final_multiplier
    fat *= final_multiplier
    carbs *= final_multiplier
    sugar *= final_multiplier

    calories += apply_rules(food_name, answers)

    return {
        'calories': int(round(calories)),
        'protein': round(protein, 1),
        'fat': round(fat, 1),
        'carbs': round(carbs, 1),
        'sugar': round(sugar, 1),
        'fiber': round(calories * 0.01, 1),
        'food_display': food_data['name'],
        'emoji': food_data['emoji']
    }

def apply_rules(food_name, answers):
    """Full rule-based logic from original version"""
    bonus = 0
    if food_name == "fried_rice":
        if answers.get("q5_style") == "street" and answers.get("q4_oil") == "oily":
            bonus += 100
        if "manchurian" in answers.get("q2_additions", []):
            bonus += 80
        if answers.get("q5_style") == "restaurant":
            bonus += 50
    if food_name == "pizza":
        if answers.get("q7_cheese") == "extra":
            bonus += 80
    if food_name == "samosa":
        if answers.get("q4_oil") == "oily":
            quantity = answers.get("q2_quantity", 1)
            if quantity in [3, '3', 3.0]:
                bonus += 50
    if food_name == "french_fries":
        if answers.get("q2_type") == "loaded":
            bonus += 60
    return bonus

def default_response(food_name):
    return {
        'calories': 200,
        'protein': 5,
        'carbs': 20,
        'fat': 10,
        'sugar': 5,
        'fiber': 1,
        'food_display': food_name.replace('_', ' ').title(),
        'emoji': '🍽️'
    }

def get_all_foods():
    return list(FOOD_QUESTIONS.keys())

def validate_answers(food_name, answers):
    food_name = food_name.lower()
    if food_name in FOOD_ALIASES:
        food_name = FOOD_ALIASES[food_name]
    if food_name not in FOOD_QUESTIONS:
        return {'valid': True, 'missing': []}
    return {'valid': True, 'missing': []}

def get_food_by_name(food_name):
    food_name = food_name.lower()
    if food_name in FOOD_ALIASES:
        food_name = FOOD_ALIASES[food_name]
    return FOOD_QUESTIONS.get(food_name)