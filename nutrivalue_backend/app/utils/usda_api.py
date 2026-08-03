import requests
import os
from typing import Dict, List, Optional


class USDANutritionAPI:
    """Wrapper for USDA FoodData Central API"""

    def __init__(self, api_key: str = None):
        # PASTE YOUR API KEY HERE 👇
        self.api_key = api_key or "8KXofwo8TWaoxfj5wwdhNkIWNiwvDaKu3aayau76"  # <-- CHANGE THIS
        self.base_url = "https://api.nal.usda.gov/fdc/v1"

    def search_food(self, query: str, page_size: int = 5) -> List[Dict]:
        """Search for foods by name"""
        url = f"{self.base_url}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": page_size,
            "dataType": ["Survey (FNDDS)", "Foundation", "SR Legacy"]
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get('foods', [])
            else:
                print(f"API Error: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error searching food: {e}")
            return []

    def get_food_nutrients(self, fdc_id: int) -> Optional[Dict]:
        """Get detailed nutrient information for a specific food"""
        url = f"{self.base_url}/food/{fdc_id}"
        params = {"api_key": self.api_key}

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def get_nutrients_by_name(self, food_name: str) -> Optional[Dict]:
        """Search and return nutrients - MAIN FUNCTION YOU'LL USE"""
        foods = self.search_food(food_name, page_size=3)

        if not foods:
            return None

        # Get the most relevant result
        best_match = foods[0]
        fdc_id = best_match['fdcId']

        # Get detailed nutrients
        details = self.get_food_nutrients(fdc_id)

        if not details:
            return None

        # Extract nutrients
        nutrients = {}
        for nutrient in details.get('foodNutrients', []):
            name = nutrient.get('nutrient', {}).get('name', '')
            value = nutrient.get('amount', 0)
            unit = nutrient.get('nutrient', {}).get('unitName', '')

            # Get important nutrients
            important = ['Energy', 'Protein', 'Total lipid', 'Carbohydrate', 'Fiber', 'Sugars', 'Sodium']
            if any(key in name for key in important):
                nutrients[name] = f"{value} {unit}"

        return {
            'food_name': details.get('description', food_name),
            'nutrients': nutrients
        }


# Create global instance
usda_api = USDANutritionAPI()