def map_food(predicted_food):
    predicted_food = predicted_food.lower()

    food_map = {
        "burger": ["burger", "cheeseburger", "hamburger", "veg burger", "chicken burger"],
        "pizza": ["pizza", "pepperoni pizza", "margherita pizza", "cheese pizza"],
        "biryani": ["biryani", "chicken biryani", "veg biryani", "mutton biryani"],
        "sandwich": ["sandwich", "club sandwich", "veg sandwich", "chicken sandwich"],
        "pasta": ["pasta", "spaghetti", "macaroni"],
        "fries": ["fries", "french fries"],
        "donut": ["donut", "doughnut"]
    }

    for general_food, variants in food_map.items():
        for variant in variants:
            if variant in predicted_food:
                return general_food

    return predicted_food  # fallback if no match
