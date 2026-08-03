from food_mapper import map_food

test_cases = [
    "cheeseburger",
    "veg burger",
    "pepperoni pizza",
    "chicken biryani",
    "club sandwich",
    "spaghetti"
]

for food in test_cases:
    print(food, "→", map_food(food))
