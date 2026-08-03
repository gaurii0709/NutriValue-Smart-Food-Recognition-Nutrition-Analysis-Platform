import pandas as pd

csv_path = r"/dataset_final\nutrition.csv"
df = pd.read_csv(csv_path)

def get_nutrition(food_name):
    food_name = food_name.strip().lower()
    df["Food"] = df["Food"].str.strip().str.lower()

    row = df[df["Food"] == food_name]

    if not row.empty:
        return row.iloc[0].to_dict()
    else:
        return f"❌ '{food_name}' not found in nutrition database"

# TEST CASES
print(get_nutrition("burger"))
print(get_nutrition("pizza"))
print(get_nutrition("biryani"))
print(get_nutrition("pasta"))
