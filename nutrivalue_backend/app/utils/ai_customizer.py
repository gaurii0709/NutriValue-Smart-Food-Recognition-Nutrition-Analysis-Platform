import json
import os
from typing import Any, Dict, Optional

import requests


class CustomOptionAI:
    """Small helper that estimates nutrition deltas for free-text custom options."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.timeout = int(os.getenv("OPENAI_TIMEOUT_SECONDS", "20"))

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def estimate_custom_option(
        self,
        *,
        food_name: str,
        question_id: str,
        question_text: str,
        custom_text: str,
    ) -> Dict[str, Any]:
        """Return a structured nutrition estimate for a custom option."""
        cleaned_text = (custom_text or "").strip()
        if not cleaned_text:
            return self._fallback_response(food_name=food_name, question_id=question_id, custom_text=custom_text)

        if not self.is_enabled():
            result = self._fallback_response(food_name=food_name, question_id=question_id, custom_text=custom_text)
            result["source"] = "fallback"
            result["message"] = "AI is not configured, so a safe fallback estimate was used."
            return result

        prompt = self._build_prompt(
            food_name=food_name,
            question_id=question_id,
            question_text=question_text,
            custom_text=cleaned_text,
        )
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You estimate only the nutrition delta for one custom food option inside a meal question. "
                        "Return valid JSON only. Keep estimates practical and conservative."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return self._normalize_response(
                parsed,
                food_name=food_name,
                question_id=question_id,
                custom_text=cleaned_text,
                source="ai",
            )
        except Exception as exc:
            result = self._fallback_response(food_name=food_name, question_id=question_id, custom_text=cleaned_text)
            result["source"] = "fallback"
            result["message"] = f"AI estimate failed, so a safe fallback estimate was used: {exc}"
            return result

    def _build_prompt(self, *, food_name: str, question_id: str, question_text: str, custom_text: str) -> str:
        return (
            "Estimate the nutrition addition for a custom answer inside a food-nutrition questionnaire.\n"
            f"Food: {food_name}\n"
            f"Question ID: {question_id}\n"
            f"Question Text: {question_text}\n"
            f"Custom user answer: {custom_text}\n\n"
            "Rules:\n"
            "- Return only the additional nutrition caused by this custom option, not the whole meal.\n"
            "- Use small realistic values for flavors, toppings, sauces, fillings, crust styles, etc.\n"
            "- If the text is mainly a flavor, keep protein/fat/carbs modest unless the flavor implies a topping mix.\n"
            "- If the text names a sauce, topping, or loaded add-on, include a realistic calorie impact.\n"
            "- If uncertain, estimate conservatively instead of zero.\n"
            "- Calories should be an integer-like number, macros can be decimals.\n\n"
            "Return JSON with this exact shape:\n"
            "{\n"
            '  "item_name": "normalized label",\n'
            '  "confidence": "high|medium|low",\n'
            '  "nutrition": {\n'
            '    "calories": 0,\n'
            '    "protein": 0,\n'
            '    "fat": 0,\n'
            '    "carbs": 0,\n'
            '    "sugar": 0\n'
            "  },\n"
            '  "reason": "short one-line reason"\n'
            "}"
        )

    def _normalize_response(
        self,
        parsed: Dict[str, Any],
        *,
        food_name: str,
        question_id: str,
        custom_text: str,
        source: str,
    ) -> Dict[str, Any]:
        nutrition = parsed.get("nutrition") or {}
        return {
            "success": True,
            "source": source,
            "food_name": food_name,
            "question_id": question_id,
            "item_name": (parsed.get("item_name") or custom_text).strip(),
            "confidence": parsed.get("confidence", "medium"),
            "reason": parsed.get("reason", "Estimated from the custom option provided by the user."),
            "nutrition": {
                "calories": int(round(float(nutrition.get("calories", 50)))),
                "protein": round(float(nutrition.get("protein", 0)), 1),
                "fat": round(float(nutrition.get("fat", 0)), 1),
                "carbs": round(float(nutrition.get("carbs", 0)), 1),
                "sugar": round(float(nutrition.get("sugar", 0)), 1),
            },
        }

    def _fallback_response(self, *, food_name: str, question_id: str, custom_text: str) -> Dict[str, Any]:
        estimate = self._fallback_estimate(custom_text)
        return {
            "success": True,
            "source": "fallback",
            "food_name": food_name,
            "question_id": question_id,
            "item_name": custom_text.strip() or "Custom option",
            "confidence": "low",
            "reason": "Used a conservative fallback estimate for a custom option.",
            "nutrition": estimate,
        }

    def _fallback_estimate(self, custom_text: str) -> Dict[str, Any]:
        text = (custom_text or "").strip().lower()
        keyword_profiles = [
            (("oreo", "cookie", "biscuit"), {"calories": 55, "protein": 1.0, "fat": 2.0, "carbs": 8.0, "sugar": 5.0}),
            (("brownie", "cake"), {"calories": 90, "protein": 1.5, "fat": 4.0, "carbs": 12.0, "sugar": 8.0}),
            (("chocolate", "choco"), {"calories": 45, "protein": 0.5, "fat": 2.0, "carbs": 6.0, "sugar": 5.0}),
            (("caramel", "butterscotch"), {"calories": 50, "protein": 0.3, "fat": 2.0, "carbs": 7.0, "sugar": 6.0}),
            (("nuts", "almond", "cashew", "pistachio"), {"calories": 70, "protein": 2.0, "fat": 6.0, "carbs": 2.0, "sugar": 0.5}),
            (("cheese", "cheesy"), {"calories": 80, "protein": 4.0, "fat": 6.0, "carbs": 2.0, "sugar": 0.0}),
            (("mayo", "mayonnaise"), {"calories": 90, "protein": 0.2, "fat": 10.0, "carbs": 1.0, "sugar": 0.0}),
            (("sauce", "dip"), {"calories": 40, "protein": 0.5, "fat": 2.0, "carbs": 5.0, "sugar": 3.0}),
            (("fruit", "berry", "mango", "strawberry", "blueberry"), {"calories": 30, "protein": 0.3, "fat": 0.0, "carbs": 7.0, "sugar": 5.0}),
        ]

        for keywords, profile in keyword_profiles:
            if any(keyword in text for keyword in keywords):
                return profile

        return {"calories": 50, "protein": 0.5, "fat": 1.5, "carbs": 7.0, "sugar": 4.0}


custom_option_ai = CustomOptionAI()
