// API service for NutriValue

const API_BASE_URL = 'http://localhost:8000'; // Change this to your backend URL

export const foodAPI = {
  // Get all available foods
  getAllFoods: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/foods`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching foods:', error);
      return { success: false, error: error.message };
    }
  },

  // Get questions for a food
  getFoodQuestions: async (foodName) => {
    try {
      const response = await fetch(`${API_BASE_URL}/food/${foodName}/questions`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching questions:', error);
      return { success: false, error: error.message };
    }
  },

  // Process answers and get nutrition
  calculateNutrition: async (foodName, answers) => {
    try {
      const formData = new URLSearchParams();
      formData.append('food_name', foodName);
      formData.append('answers', JSON.stringify(answers));

      const response = await fetch(`${API_BASE_URL}/questions/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
      });
      return await response.json();
    } catch (error) {
      console.error('Error calculating nutrition:', error);
      return { success: false, error: error.message };
    }
  },

  // Complete flow with image upload
  completeFlow: async (file, foodName = null, answers = {}) => {
    try {
      const formData = new FormData();
      if (file) formData.append('file', file);
      if (foodName) formData.append('food_name', foodName);
      formData.append('answers', JSON.stringify(answers));

      const response = await fetch(`${API_BASE_URL}/complete-flow`, {
        method: 'POST',
        body: formData
      });
      return await response.json();
    } catch (error) {
      console.error('Error in complete flow:', error);
      return { success: false, error: error.message };
    }
  }
};