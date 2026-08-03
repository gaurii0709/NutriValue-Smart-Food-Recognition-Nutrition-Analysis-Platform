import { useState, useRef, useEffect, useCallback } from "react";
import Webcam from "react-webcam";
import confetti from "canvas-confetti";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Toaster, toast } from 'sonner';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";

function App() {
  // ============================================
  // AUTHENTICATION STATE
  // ============================================
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [authToken, setAuthToken] = useState(null);
  const [userEmail, setUserEmail] = useState("");
  const [showAuthModal, setShowAuthModal] = useState(true);
  const [authMode, setAuthMode] = useState("login");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);

  // ============================================
  // PROFILE STATE
  // ============================================
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profile, setProfile] = useState(null);
  const [profileForm, setProfileForm] = useState({
    height_cm: "",
    weight_kg: "",
    age: "",
    gender: "",
    activity_level: "",
    goal: ""
  });
  const [dailyProgress, setDailyProgress] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);

  // ============================================
  // MEAL HISTORY STATE
  // ============================================
  const [showHistory, setShowHistory] = useState(false);
  const [mealHistory, setMealHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [filteredMeals, setFilteredMeals] = useState([]);
  const [showAnalytics, setShowAnalytics] = useState(false);

  // ============================================
  // EXISTING STATE (no custom input)
  // ============================================
  const [messages, setMessages] = useState([]);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showWebcam, setShowWebcam] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [detectedFood, setDetectedFood] = useState(null);
  const [result, setResult] = useState(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [currentMultiSelections, setCurrentMultiSelections] = useState({});
  const [currentQuestionObj, setCurrentQuestionObj] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const webcamRef = useRef(null);
  const messagesEndRef = useRef(null);
  const fileUploadRef = useRef(null);
  const mobileCameraRef = useRef(null);

  // ============================================
  // CHARTS HELPERS (ADDED – MISSING BEFORE)
  // ============================================
  const getChartData = () => {
    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toDateString();
      const dayMeals = mealHistory.filter(meal =>
        new Date(meal.created_at).toDateString() === dateStr
      );
      const totalCalories = dayMeals.reduce((sum, meal) => sum + (meal.nutrition?.calories || 0), 0);
      last7Days.push({
        date: date.toLocaleDateString('en-US', { weekday: 'short' }),
        calories: totalCalories,
        fullDate: dateStr
      });
    }
    return last7Days;
  };

  const getMacroData = () => {
    const totalProtein = mealHistory.reduce((sum, meal) => sum + (meal.nutrition?.protein || 0), 0);
    const totalCarbs = mealHistory.reduce((sum, meal) => sum + (meal.nutrition?.carbs || 0), 0);
    const totalFat = mealHistory.reduce((sum, meal) => sum + (meal.nutrition?.fat || 0), 0);
    return [
      { name: 'Protein', value: totalProtein, color: '#3b82f6' },
      { name: 'Carbs', value: totalCarbs, color: '#eab308' },
      { name: 'Fat', value: totalFat, color: '#a855f7' }
    ];
  };

  const COLORS = ['#3b82f6', '#eab308', '#a855f7'];

  // ============================================
  // Filter meals by selected date
  // ============================================
  useEffect(() => {
    if (mealHistory.length > 0) {
      const filtered = mealHistory.filter(meal => {
        const mealDate = new Date(meal.created_at).toDateString();
        const selectedDateStr = selectedDate.toDateString();
        return mealDate === selectedDateStr;
      });
      setFilteredMeals(filtered);
    } else {
      setFilteredMeals([]);
    }
  }, [mealHistory, selectedDate]);

  // ============================================
  // TOKEN VALIDATION FUNCTION
  // ============================================
  const validateToken = async (token) => {
    try {
      const res = await fetch(`http://localhost:8000/api/auth/me?token=${token}`);
      const data = await res.json();
      return data.success === true;
    } catch (error) {
      return false;
    }
  };

  // Load user profile after login (called only when token is valid)
  const loadUserProfile = useCallback(async (token) => {
    try {
      const res = await fetch(`http://localhost:8000/api/profile/get?token=${token}`);
      const data = await res.json();
      if (data.success && data.profile) {
        setProfile(data.profile);
        const progressRes = await fetch(`http://localhost:8000/api/profile/daily-progress?token=${token}`);
        const progressData = await progressRes.json();
        if (progressData.success) {
          setDailyProgress(progressData);
        }
      } else {
        // No profile found → show profile modal
        setShowProfileModal(true);
      }
    } catch (error) {
      console.error("Error loading profile:", error);
      // If the token is invalid, force logout
      handleLogout();
    }
  }, []);

  // Check for saved token on load → validate it first
  useEffect(() => {
    const savedToken = localStorage.getItem("authToken");
    const savedEmail = localStorage.getItem("userEmail");
    if (savedToken) {
      validateToken(savedToken).then(isValid => {
        if (isValid) {
          setAuthToken(savedToken);
          setUserEmail(savedEmail || "");
          setIsLoggedIn(true);
          setShowAuthModal(false);
          loadUserProfile(savedToken);
        } else {
          // Token invalid or expired → clear storage and show login
          localStorage.removeItem("authToken");
          localStorage.removeItem("userEmail");
          setShowAuthModal(true);
          setIsLoggedIn(false);
        }
      });
    } else {
      setShowAuthModal(true);
    }
  }, [loadUserProfile]);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Confetti effect
  useEffect(() => {
    if (result && !showConfetti) {
      setShowConfetti(true);
      confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
      setTimeout(() => confetti({ particleCount: 100, spread: 100, origin: { y: 0.5, x: 0.3 } }), 200);
      setTimeout(() => confetti({ particleCount: 100, spread: 100, origin: { y: 0.5, x: 0.7 } }), 400);
      if (authToken) {
        const refreshProgress = async () => {
          const res = await fetch(`http://localhost:8000/api/profile/daily-progress?token=${authToken}`);
          const data = await res.json();
          if (data.success) setDailyProgress(data);
        };
        refreshProgress();
      }
    }
  }, [result, showConfetti, authToken]);

  // Add initial bot message (only when not in auth/profile modals)
  useEffect(() => {
    if (!showAuthModal && !showProfileModal) {
      setMessages([
        {
          id: Date.now(),
          type: "bot",
          content: "👋 Hey there! I'm your nutrition assistant. What's on your plate today?",
          options: [
            { label: "📸 Take a photo", action: "camera" },
            { label: "📁 Upload from gallery", action: "upload" }
          ]
        }
      ]);
    }
  }, [showAuthModal, showProfileModal]);

  // ============================================
  // AUTHENTICATION FUNCTIONS
  // ============================================

  const handleAuth = async () => {
    setAuthError("");
    setAuthLoading(true);

    const endpoint = authMode === "login" ? "/api/auth/login" : "/api/auth/signup";

    try {
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `email=${encodeURIComponent(authEmail)}&password=${encodeURIComponent(authPassword)}`
      });

      const data = await res.json();

      if (data.success) {
        if (authMode === "login") {
          setAuthToken(data.access_token);
          setUserEmail(authEmail);
          setIsLoggedIn(true);
          localStorage.setItem("authToken", data.access_token);
          localStorage.setItem("userEmail", authEmail);
          setShowAuthModal(false);
          loadUserProfile(data.access_token);
          toast.success('Login successful! Welcome back! 🎉');
        } else {
          setAuthMode("login");
          setAuthError("Account created! Please check your email to verify, then login.");
          toast.info('Account created! Please verify your email.');
        }
      } else {
        setAuthError(data.error || "Authentication failed");
        toast.error(data.error || "Authentication failed");
      }
    } catch (error) {
      setAuthError("Network error. Please try again.");
      toast.error("Network error. Please try again.");
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("userEmail");
    setAuthToken(null);
    setUserEmail("");
    setIsLoggedIn(false);
    setProfile(null);
    setDailyProgress(null);
    setShowAuthModal(true);
    setResult(null);
    setMessages([]);
    toast.success('Logged out successfully!');
  };

  // Save user profile
  const saveUserProfile = async () => {
    if (!profileForm.height_cm || !profileForm.weight_kg || !profileForm.age || !profileForm.gender || !profileForm.activity_level || !profileForm.goal) {
      toast.error("Please fill all fields");
      return;
    }

    setProfileLoading(true);

    const formData = new URLSearchParams();
    formData.append("token", authToken);
    formData.append("height_cm", profileForm.height_cm);
    formData.append("weight_kg", profileForm.weight_kg);
    formData.append("age", profileForm.age);
    formData.append("gender", profileForm.gender);
    formData.append("activity_level", profileForm.activity_level);
    formData.append("goal", profileForm.goal);

    try {
      const res = await fetch("http://localhost:8000/api/profile/save", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData
      });

      const data = await res.json();
      if (data.success) {
        setProfile(data.profile);
        setShowProfileModal(false);
        try {
          const progressRes = await fetch(`http://localhost:8000/api/profile/daily-progress?token=${authToken}`);
          const progressData = await progressRes.json();
          if (progressData.success) setDailyProgress(progressData);
        } catch (e) {
          console.log("Progress fetch error:", e);
        }
        addMessage("bot", `🎉 Profile saved! Your daily calorie goal is ${data.daily_calorie_goal} calories.`, null);
        toast.success(`Profile saved! Daily goal: ${data.daily_calorie_goal} calories`);
      } else {
        toast.error(data.error || "Failed to save profile");
      }
    } catch (error) {
      console.error("Error saving profile:", error);
      toast.error("Network error while saving profile");
    } finally {
      setProfileLoading(false);
    }
  };

  // ============================================
  // MEAL HISTORY FUNCTIONS
  // ============================================

  const saveCurrentMeal = async () => {
    if (isSaving) return;
    if (!result || !detectedFood || !authToken) {
      toast.warning("No meal to save or you need to login first!");
      return;
    }

    setIsSaving(true);
    setLoading(true);
    addMessage("bot", "Saving your meal to history... 💾", null);

    try {
      const formData = new URLSearchParams();
      formData.append("token", authToken);
      formData.append("food_name", detectedFood);
      formData.append("calories", result.calories || 0);
      formData.append("protein", result.protein || 0);
      formData.append("carbs", result.carbs || 0);
      formData.append("fat", result.fat || 0);
      formData.append("sugar", result.sugar || 0);
      formData.append("answers", JSON.stringify(answers));

      const res = await fetch("http://localhost:8000/api/meals/save", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData
      });

      const data = await res.json();

      if (data.success) {
        addMessage("bot", "✅ Meal saved to your history! View it from the History button.", null);
        toast.success(`✅ ${detectedFood} saved to history!`);
        const progressRes = await fetch(`http://localhost:8000/api/profile/daily-progress?token=${authToken}`);
        const progressData = await progressRes.json();
        if (progressData.success) setDailyProgress(progressData);
      } else {
        addMessage("bot", `❌ Failed to save: ${data.error}`, null);
        toast.error("Failed to save meal");
      }
    } catch (error) {
      addMessage("bot", "❌ Network error while saving.", null);
      toast.error("Network error while saving");
    } finally {
      setIsSaving(false);
      setLoading(false);
    }
  };

  const loadMealHistory = async () => {
    if (!authToken) return;

    setHistoryLoading(true);
    setShowHistory(true);
    setShowAnalytics(false);

    try {
      const res = await fetch(`http://localhost:8000/api/meals/history?token=${authToken}&limit=50`);
      const data = await res.json();

      if (data.success) {
        setMealHistory(data.meals);
        setFilteredMeals(data.meals);
        toast.success(`Loaded ${data.meals.length} meals`);
      } else {
        setMealHistory([]);
      }
    } catch (error) {
      setMealHistory([]);
      toast.error("Error loading history");
    } finally {
      setHistoryLoading(false);
    }
  };

  const deleteMeal = async (mealId) => {
    if (!authToken) return;

    try {
      const res = await fetch(`http://localhost:8000/api/meals/delete/${mealId}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `token=${authToken}`
      });

      const data = await res.json();
      if (data.success) {
        setMealHistory(mealHistory.filter(meal => meal.id !== mealId));
        addMessage("bot", "🗑️ Meal deleted from history.", null);
        toast.success("Meal deleted successfully");
        const progressRes = await fetch(`http://localhost:8000/api/profile/daily-progress?token=${authToken}`);
        const progressData = await progressRes.json();
        if (progressData.success) setDailyProgress(progressData);
      }
    } catch (error) {
      console.error("Delete failed:", error);
      toast.error("Failed to delete meal");
    }
  };

  // ============================================
  // EXISTING FUNCTIONS (unchanged)
  // ============================================

  const addMessage = (type, content, options = null, imagePreview = null) => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: type,
      content: content,
      options: options,
      imagePreview: imagePreview
    }]);
  };

  const resetChat = () => {
    setPreview(null);
    setQuestions([]);
    setAnswers({});
    setCurrentQuestionIndex(0);
    setDetectedFood(null);
    setResult(null);
    setShowConfetti(false);
    setCurrentMultiSelections({});
    setCurrentQuestionObj(null);
    setLoading(false);

    setMessages([
      {
        id: Date.now(),
        type: "bot",
        content: "👋 Hey there! I'm your nutrition assistant. What's on your plate today?",
        options: [
          { label: "📸 Take a photo", action: "camera" },
          { label: "📁 Upload from gallery", action: "upload" }
        ]
      }
    ]);
  };

  const handleUserAction = (action) => {
    if (action === "camera") {
      setShowWebcam(true);
    } else if (action === "upload") {
      fileUploadRef.current?.click();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleImageUpload(file);
    }
  };

  const captureFromWebcam = () => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      fetch(imageSrc)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], "webcam_capture.jpg", { type: "image/jpeg" });
          handleImageUpload(file);
          setShowWebcam(false);
        });
    }
  };

  const handleImageUpload = async (file) => {
    const previewUrl = URL.createObjectURL(file);
    setPreview(previewUrl);

    addMessage("user", "📷 Here's my meal!", null, previewUrl);
    addMessage("bot", "Let me analyze that for you... 🔍", null);

    setLoading(true);
    toast.info("Analyzing your meal...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/api/complete-flow", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!data.success && data.error && data.error.includes("Could not identify")) {
        addMessage("bot", data.error, [
          { label: "📸 Try Another Photo", action: "retry" },
          { label: "🏠 Start Over", action: "home" }
        ]);
        toast.error("Could not identify food. Try another photo!");
        setLoading(false);
        return;
      }

      if (data.success && data.stage === 'questions') {
        setDetectedFood(data.food);
        setQuestions(data.questions);
        setCurrentQuestionIndex(0);
        setAnswers({});
        setCurrentMultiSelections({});

        const foodEmoji = getFoodEmoji(data.food);
        addMessage("bot", `I can see that's ${data.food_display}! ${foodEmoji}\n\nLet me ask you a few quick questions.`, null);

        const firstQuestion = data.questions[0];
        if (firstQuestion) {
          askNextQuestion(firstQuestion, {});
        }
        toast.success(`Detected: ${data.food_display}`);
      } else {
        addMessage("bot", "Hmm, I couldn't recognize that food. Could you try another photo? 📸", [
          { label: "📸 Try Again", action: "retry" },
          { label: "🏠 Start Over", action: "home" }
        ]);
        toast.error("Could not recognize food. Please try again.");
      }
    } catch (error) {
      console.error("Upload error:", error);
      addMessage("bot", "Sorry, something went wrong. Please try again! 😅", [
        { label: "🔄 Retry", action: "retry" },
        { label: "🏠 Start Over", action: "home" }
      ]);
      toast.error("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const shouldShowQuestion = (question, currentAnswers) => {
    if (!question.condition) return true;

    for (const [key, value] of Object.entries(question.condition)) {
      const rawAnswer = currentAnswers[key];
      const userAnswer = rawAnswer?.selected_value ?? rawAnswer;
      if (!userAnswer) return false;
      if (Array.isArray(value)) {
        if (!value.includes(userAnswer)) return false;
      } else {
        if (userAnswer !== value) return false;
      }
    }
    return true;
  };

  const filterOptionsByConditions = (options, currentAnswers) => {
    if (!options || !currentAnswers) return options;

    return options.filter(opt => {
      if (!opt.condition) return true;
      for (const [key, value] of Object.entries(opt.condition)) {
        const rawAnswer = currentAnswers[key];
        const userAnswer = rawAnswer?.selected_value ?? rawAnswer;
        // 🔥 FIX: hide option if condition not yet answered
        if (!userAnswer) return false;
        if (Array.isArray(value)) {
          if (!value.includes(userAnswer)) return false;
        } else {
          if (userAnswer !== value) return false;
        }
      }
      return true;
    });
  };

  const askNextQuestion = (question, currentAnswers) => {
  setCurrentQuestionObj(question);

  if (!shouldShowQuestion(question, currentAnswers)) {
    handleNextQuestion(currentAnswers);
    return;
  }

  if (question.type === 'single_select') {
    const filteredOptions = filterOptionsByConditions(question.options, currentAnswers);
    if (filteredOptions.length === 0) {
      handleNextQuestion(currentAnswers);
      return;
    }
    const options = filteredOptions.map(opt => ({
      label: opt.label,
      value: opt.value,
      questionId: question.id,
      nutrition: opt.nutrition,
      multiplier: opt.multiplier,
      portion_multiplier: opt.portion_multiplier,
      final_multiplier: opt.final_multiplier
    }));
    addMessage("bot", question.text, options);
  }
  else if (question.type === 'multi_select') {
    const filteredOptions = filterOptionsByConditions(question.options, currentAnswers);
    const options = filteredOptions.map(opt => ({
      label: opt.label,
      value: opt.value,
      questionId: question.id,
      isMulti: true,
      nutrition: opt.nutrition
    }));
    if (options.length === 0) {
      handleNextQuestion(currentAnswers);
      return;
    }
    setCurrentMultiSelections(prev => ({ ...prev, [question.id]: currentAnswers[question.id] || [] }));
    addMessage("bot", `${question.text} (Tap to select multiple)`, options);
  }
  else if (question.type === 'number_input') {
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: "bot",
      content: question.text,
      numberInput: question
    }]);
  }
};

 const handleAnswer = async (option, isMulti = false) => {
  const qid = option.questionId;
  let newAnswers = { ...answers };

  if (isMulti) {
    let currentMulti = newAnswers[qid] || [];
    if (currentMulti.includes(option.value)) {
      currentMulti = currentMulti.filter(v => v !== option.value);
    } else {
      currentMulti.push(option.value);
    }
    newAnswers[qid] = currentMulti;
    setAnswers(newAnswers);
    setCurrentMultiSelections(prev => ({ ...prev, [qid]: currentMulti }));
    addMessage("user", `Selected: ${option.label}`, null);
    return;
  } else {
    newAnswers[qid] = option.value;
    setAnswers(newAnswers);
    addMessage("user", option.label, null);
  }

  let nextIndex = currentQuestionIndex + 1;
  while (nextIndex < questions.length) {
    const nextQuestion = questions[nextIndex];
    if (shouldShowQuestion(nextQuestion, newAnswers)) {
      setCurrentQuestionIndex(nextIndex);
      askNextQuestion(nextQuestion, newAnswers);
      return;
    }
    nextIndex++;
  }
  await submitAllAnswers(newAnswers);
};

  const handleNumberSubmit = async (value, questionId) => {
  const newAnswers = { ...answers, [questionId]: value };
  setAnswers(newAnswers);
  addMessage("user", `${value}`, null);

  let nextIndex = currentQuestionIndex + 1;
  while (nextIndex < questions.length) {
    const nextQuestion = questions[nextIndex];
    if (shouldShowQuestion(nextQuestion, newAnswers)) {
      setCurrentQuestionIndex(nextIndex);
      askNextQuestion(nextQuestion, newAnswers);
      return;
    }
    nextIndex++;
  }
  await submitAllAnswers(newAnswers);
};

  const handleMultiSelectNext = () => {
  const qid = currentQuestionObj?.id;
  const selected = currentMultiSelections[qid] || [];

  if (selected.length === 0) {
    addMessage("bot", "Please select at least one option!", null);
    return;
  }

  const currentAnswers = { ...answers, [qid]: selected };

  let nextIndex = currentQuestionIndex + 1;
  while (nextIndex < questions.length) {
    const nextQuestion = questions[nextIndex];
    if (shouldShowQuestion(nextQuestion, currentAnswers)) {
      setCurrentQuestionIndex(nextIndex);
      askNextQuestion(nextQuestion, currentAnswers);
      return;
    }
    nextIndex++;
  }
  submitAllAnswers(currentAnswers);
};

 const handleNextQuestion = (currentAnswers) => {
  let nextIndex = currentQuestionIndex + 1;
  while (nextIndex < questions.length) {
    const nextQuestion = questions[nextIndex];
    if (shouldShowQuestion(nextQuestion, currentAnswers)) {
      setCurrentQuestionIndex(nextIndex);
      askNextQuestion(nextQuestion, currentAnswers);
      return;
    }
    nextIndex++;
  }
  submitAllAnswers(currentAnswers);
};

  const submitAllAnswers = async (finalAnswers) => {
    setLoading(true);
    addMessage("bot", "Calculating your nutrition... 📊", null);
    toast.info("Calculating nutrition...");

    const formData = new URLSearchParams();
    formData.append('food_name', detectedFood);
    formData.append('answers', JSON.stringify(finalAnswers));

    try {
      const res = await fetch("http://localhost:8000/api/questions/process", {
        method: "POST",
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      const data = await res.json();

      if (data.success) {
        setResult(data.nutrition);
        showNutritionResult(data.nutrition);
        toast.success("Nutrition calculated!");
      } else {
        addMessage("bot", "Sorry, I couldn't calculate the nutrition. Please try again! 😅", null);
        toast.error("Could not calculate nutrition");
      }
    } catch (error) {
      console.error("Submit error:", error);
      addMessage("bot", "Something went wrong. Please try again! 🔄", null);
      toast.error("Network error");
    } finally {
      setLoading(false);
    }
  };

  const getNutritionTip = (nutrition, food) => {
    const tips = [
      { condition: nutrition?.protein > 20, tip: "💪 High in protein! Great for muscle building!" },
      { condition: nutrition?.fiber > 5, tip: "🌾 Excellent fiber content! Good for digestion." },
      { condition: nutrition?.calories < 300, tip: "🥗 Light meal! Perfect for weight management." },
      { condition: nutrition?.calories > 800, tip: "⚡ High calorie meal. Great for active days!" },
      { condition: nutrition?.fat > 25, tip: "🧈 Rich in fats. Enjoy in moderation." },
      { condition: nutrition?.sugar > 20, tip: "🍬 High in sugar. Consider reducing sweet toppings." },
      { condition: food === 'pizza', tip: "🍕 Try adding veggies to your pizza for extra nutrients!" },
      { condition: food === 'burger', tip: "🍔 Consider whole grain buns for more fiber!" },
      { condition: food === 'ice_cream', tip: "🍦 Try frozen yogurt for a lighter alternative with less sugar!" },
      { condition: food === 'samosa', tip: "🥟 Bake instead of fry to reduce calories by 40%!" },
      { condition: food === 'french_fries', tip: "🍟 Air fryer fries save 50% of the calories!" },
    ];

    const matchingTip = tips.find(tip => tip.condition);
    return matchingTip ? matchingTip.tip : "🥗 Balanced eating is key to a healthy lifestyle!";
  };

  const showNutritionResult = (nutrition) => {
    const foodEmoji = getFoodEmoji(detectedFood);
    const foodName = nutrition.food_display || detectedFood?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Your Meal';

    const ResultCard = () => (
      <div className="space-y-3">
        <div className="flex items-center justify-between bg-white rounded-xl p-3 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <div className="text-3xl">{foodEmoji}</div>
            <div>
              <div className="font-semibold text-gray-800 text-sm">{foodName}</div>
              <div className="text-xs text-gray-400">Nutrition analysis</div>
            </div>
          </div>
        </div>

        {dailyProgress && (
          <div className="bg-blue-50 rounded-xl p-3 border border-blue-100">
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>Today's Progress</span>
              <span>{dailyProgress.consumed} / {dailyProgress.daily_goal} cal</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, dailyProgress.percentage)}%` }}
              />
            </div>
            <div className="text-[11px] text-gray-500 mt-2">
              {dailyProgress.tip}
            </div>
          </div>
        )}

        <div className="overflow-x-auto pb-2 -mx-1 px-1">
          <div className="flex gap-2 min-w-max">
            <div className="bg-white rounded-xl p-2 text-center shadow-sm border border-gray-100 w-20">
              <div className="text-red-500 text-lg">🔥</div>
              <div className="font-bold text-gray-800 text-sm">{nutrition.calories || 0}</div>
              <div className="text-[10px] text-gray-400">kcal</div>
            </div>
            <div className="bg-white rounded-xl p-2 text-center shadow-sm border border-gray-100 w-20">
              <div className="text-blue-500 text-lg">💪</div>
              <div className="font-bold text-gray-800 text-sm">{nutrition.protein || 0}g</div>
              <div className="text-[10px] text-gray-400">protein</div>
            </div>
            <div className="bg-white rounded-xl p-2 text-center shadow-sm border border-gray-100 w-20">
              <div className="text-yellow-500 text-lg">🍚</div>
              <div className="font-bold text-gray-800 text-sm">{nutrition.carbs || 0}g</div>
              <div className="text-[10px] text-gray-400">carbs</div>
            </div>
            <div className="bg-white rounded-xl p-2 text-center shadow-sm border border-gray-100 w-20">
              <div className="text-purple-500 text-lg">🧈</div>
              <div className="font-bold text-gray-800 text-sm">{nutrition.fat || 0}g</div>
              <div className="text-[10px] text-gray-400">fat</div>
            </div>
            <div className="bg-white rounded-xl p-2 text-center shadow-sm border border-gray-100 w-20">
              <div className="text-pink-500 text-lg">🍬</div>
              <div className="font-bold text-gray-800 text-sm">{nutrition.sugar || 0}g</div>
              <div className="text-[10px] text-gray-400">sugar</div>
            </div>
          </div>
        </div>

        {(nutrition.sugar || 0) > 20 && (
          <div className="flex items-center gap-2 bg-pink-50 rounded-xl p-2 border border-pink-100">
            <span className="text-sm">⚠️</span>
            <p className="text-[11px] text-pink-700 flex-1">High sugar content ({nutrition.sugar}g). Consider reducing sweet items.</p>
          </div>
        )}

        <div className="flex items-center gap-2 bg-amber-50 rounded-xl p-2 border border-amber-100">
          <span className="text-sm">💡</span>
          <p className="text-[11px] text-gray-600 flex-1">{getNutritionTip(nutrition, detectedFood)}</p>
        </div>
      </div>
    );

    setMessages(prev => [...prev, {
      id: Date.now(),
      type: "bot",
      component: ResultCard
    }]);

    addMessage("bot", "✨ Another meal? ✨", [
      { label: "📸 New Meal", action: "new" },
      { label: "🏠 Home", action: "home" }
    ]);
  };

  const getFoodEmoji = (foodName) => {
    if (!foodName) return '🍽️';
    const emojiMap = {
      'pizza': '🍕', 'hamburger': '🍔', 'burger': '🍔', 'fried_rice': '🍚',
      'ice_cream': '🍦', 'cheesecake': '🍰', 'samosa': '🥟', 'french_fries': '🍟'
    };
    const lowerName = foodName.toLowerCase();
    for (const [key, emoji] of Object.entries(emojiMap)) {
      if (lowerName.includes(key)) return emoji;
    }
    return '🍽️';
  };

  const NumberInputComponent = ({ question, onSubmit }) => {
    const [value, setValue] = useState(1);
    return (
      <div className="flex items-center gap-3 mt-2">
        <button onClick={() => setValue(Math.max(1, value - 1))} className="w-10 h-10 rounded-full bg-gray-200 text-xl hover:bg-gray-300 transition">-</button>
        <input type="number" value={value} onChange={(e) => setValue(parseInt(e.target.value) || 1)} className="w-20 p-2 border rounded-xl text-center text-lg" />
        <button onClick={() => setValue(Math.min(10, value + 1))} className="w-10 h-10 rounded-full bg-gray-200 text-xl hover:bg-gray-300 transition">+</button>
        <button onClick={() => onSubmit(value, question.id)} className="px-4 py-2 bg-green-500 text-white rounded-xl hover:bg-green-600 transition">OK</button>
      </div>
    );
  };

  // ============================================
  // RENDER
  // ============================================

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">

      {/* Toaster for Toast Notifications */}
      <Toaster position="top-right" richColors />

      {/* Header */}
      <div className="bg-white/80 backdrop-blur-lg border-b border-orange-100 px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center justify-between max-w-lg mx-auto">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center">
              <span className="text-xl">🍽️</span>
            </div>
            <div>
              <h1 className="font-bold text-gray-800">NutriValue</h1>
              <p className="text-xs text-gray-500">
                {isLoggedIn ? `Welcome, ${userEmail.split('@')[0]}` : "Nutrition Assistant"}
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            {isLoggedIn && (
              <button
                onClick={loadMealHistory}
                className="text-gray-500 text-sm px-3 py-1 rounded-full bg-gray-100 hover:bg-gray-200 transition"
              >
                📋 History
              </button>
            )}
            <button
              onClick={isLoggedIn ? handleLogout : () => setShowAuthModal(true)}
              className="text-gray-500 text-sm px-3 py-1 rounded-full bg-gray-100 hover:bg-gray-200 transition"
            >
              {isLoggedIn ? "Logout" : "Login"}
            </button>
            <button onClick={resetChat} className="text-gray-500 text-sm px-3 py-1 rounded-full bg-gray-100 hover:bg-gray-200 transition">
              New Chat
            </button>
          </div>
        </div>
      </div>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full">
            <div className="text-center mb-6">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center mx-auto mb-3">
                <span className="text-3xl">🍽️</span>
              </div>
              <h2 className="text-xl font-bold text-gray-800">
                {authMode === "login" ? "Welcome Back!" : "Create Account"}
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                {authMode === "login" ? "Login to save your meals" : "Sign up to track your nutrition history"}
              </p>
            </div>

            {authError && (
              <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-xl border border-red-200">
                {authError}
              </div>
            )}

            <input
              type="email"
              placeholder="Email"
              value={authEmail}
              onChange={(e) => setAuthEmail(e.target.value)}
              className="w-full p-3 border border-gray-200 rounded-xl mb-3 focus:outline-none focus:border-orange-400"
            />
            <input
              type="password"
              placeholder="Password (min 6 characters)"
              value={authPassword}
              onChange={(e) => setAuthPassword(e.target.value)}
              className="w-full p-3 border border-gray-200 rounded-xl mb-4 focus:outline-none focus:border-orange-400"
            />

            <button
              onClick={handleAuth}
              disabled={authLoading}
              className="w-full py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl font-semibold mb-3 hover:shadow-lg transition"
            >
              {authLoading ? "Processing..." : (authMode === "login" ? "Login" : "Sign Up")}
            </button>

            <p className="text-center text-sm text-gray-500">
              {authMode === "login" ? "Don't have an account? " : "Already have an account? "}
              <button
                onClick={() => {
                  setAuthMode(authMode === "login" ? "signup" : "login");
                  setAuthError("");
                }}
                className="text-orange-500 font-medium"
              >
                {authMode === "login" ? "Sign Up" : "Login"}
              </button>
            </p>
          </div>
        </div>
      )}

      {/* Profile Setup Modal (unchanged) */}
      {showProfileModal && isLoggedIn && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
          <div className="bg-white rounded-2xl w-full max-w-md overflow-hidden shadow-xl">
            <div className="border-l-4 border-orange-500 px-6 py-4 bg-white">
              <h2 className="text-xl font-semibold text-gray-800">Complete your profile</h2>
              <p className="text-sm text-gray-500 mt-0.5">For personalized nutrition recommendations</p>
            </div>

            <div className="p-6 space-y-5">
              {/* Height & Weight */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Height</label>
                  <div className="relative">
                    <input
                      type="number"
                      placeholder="Enter height"
                      value={profileForm.height_cm}
                      onChange={(e) => setProfileForm({...profileForm, height_cm: e.target.value})}
                      className="w-full px-3 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:border-orange-300 focus:ring-1 focus:ring-orange-200 transition"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">cm</span>
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Weight</label>
                  <div className="relative">
                    <input
                      type="number"
                      placeholder="Enter weight"
                      value={profileForm.weight_kg}
                      onChange={(e) => setProfileForm({...profileForm, weight_kg: e.target.value})}
                      className="w-full px-3 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:border-orange-300 focus:ring-1 focus:ring-orange-200 transition"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">kg</span>
                  </div>
                </div>
              </div>

              {/* Age */}
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Age</label>
                <input
                  type="number"
                  placeholder="Enter age"
                  value={profileForm.age}
                  onChange={(e) => setProfileForm({...profileForm, age: e.target.value})}
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:border-orange-300 focus:ring-1 focus:ring-orange-200 transition"
                />
              </div>

              {/* Gender */}
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-2">Gender</label>
                <div className="flex gap-3 flex-wrap">
                  <button
                    type="button"
                    onClick={() => setProfileForm({...profileForm, gender: 'female'})}
                    className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-all min-w-[80px] ${
                      profileForm.gender === 'female'
                        ? 'bg-orange-500 text-white shadow-sm'
                        : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100'
                    }`}
                  >
                    Female
                  </button>
                  <button
                    type="button"
                    onClick={() => setProfileForm({...profileForm, gender: 'male'})}
                    className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-all min-w-[80px] ${
                      profileForm.gender === 'male'
                        ? 'bg-orange-500 text-white shadow-sm'
                        : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100'
                    }`}
                  >
                    Male
                  </button>
                </div>
              </div>

              {/* Activity Level */}
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Activity Level</label>
                <select
                  value={profileForm.activity_level || ""}
                  onChange={(e) => setProfileForm({...profileForm, activity_level: e.target.value})}
                  className="w-full px-3 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:border-orange-300 focus:ring-1 focus:ring-orange-200 text-sm bg-white"
                >
                  <option value="" disabled>Select activity level</option>
                  <option value="sedentary">🪑 Sedentary (little or no exercise)</option>
                  <option value="light">🚶 Light (exercise 1-3 days/week)</option>
                  <option value="moderate">🏋️ Moderate (exercise 3-5 days/week)</option>
                  <option value="active">🏃 Active (exercise 6-7 days/week)</option>
                  <option value="very_active">⚡ Very Active (physical job + daily exercise)</option>
                </select>
              </div>

              {/* Goal */}
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-2">Your Goal</label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => setProfileForm({...profileForm, goal: 'lose'})}
                    className={`py-2 rounded-xl text-sm font-medium transition-all ${
                      profileForm.goal === 'lose'
                        ? 'bg-orange-500 text-white'
                        : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100'
                    }`}
                  >
                    Lose
                  </button>
                  <button
                    type="button"
                    onClick={() => setProfileForm({...profileForm, goal: 'maintain'})}
                    className={`py-2 rounded-xl text-sm font-medium transition-all ${
                      profileForm.goal === 'maintain'
                        ? 'bg-emerald-500 text-white'
                        : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100'
                    }`}
                  >
                    Maintain
                  </button>
                  <button
                    type="button"
                    onClick={() => setProfileForm({...profileForm, goal: 'gain'})}
                    className={`py-2 rounded-xl text-sm font-medium transition-all ${
                      profileForm.goal === 'gain'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-50 text-gray-600 border border-gray-200 hover:bg-gray-100'
                    }`}
                  >
                    Gain
                  </button>
                </div>
              </div>
            </div>

            <div className="border-t border-gray-100 px-6 py-4 bg-gray-50/30">
              <button
                onClick={saveUserProfile}
                disabled={profileLoading || !profileForm.height_cm || !profileForm.weight_kg || !profileForm.age || !profileForm.gender || !profileForm.activity_level || !profileForm.goal}
                className="w-full py-2.5 bg-orange-500 text-white rounded-xl font-medium hover:bg-orange-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {profileLoading ? "Saving..." : "Continue"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Meal History Modal (unchanged) */}
      {showHistory && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-md max-h-[85vh] overflow-y-auto shadow-xl">
            <div className="sticky top-0 bg-white border-b border-gray-100 px-5 py-4">
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-lg font-semibold text-gray-800">Meal History</h2>
                  <p className="text-xs text-gray-400 mt-0.5">{mealHistory.length} meals tracked</p>
                </div>
                <button onClick={() => setShowHistory(false)} className="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
              </div>
            </div>

            {mealHistory.length > 0 && (
              <div className="px-5 pt-4">
                <button
                  onClick={() => setShowAnalytics(!showAnalytics)}
                  className="w-full py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-100 transition flex items-center justify-center gap-2"
                >
                  📊 {showAnalytics ? "Hide Analytics" : "View Analytics"}
                </button>
              </div>
            )}

            {showAnalytics && mealHistory.length > 0 && (
              <div className="px-5 pt-4 space-y-4">
                <div className="bg-gray-50 rounded-xl p-3">
                  <h3 className="text-xs font-medium text-gray-500 mb-2">Weekly Calorie Trend</h3>
                  <ResponsiveContainer width="100%" height={140}>
                    <LineChart data={getChartData()}>
                      <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Line type="monotone" dataKey="calories" stroke="#f97316" strokeWidth={2} dot={{ fill: '#f97316', r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <div className="bg-gray-50 rounded-xl p-3">
                  <h3 className="text-xs font-medium text-gray-500 mb-2">Macro Distribution</h3>
                  <ResponsiveContainer width="100%" height={140}>
                    <PieChart>
                      <Pie data={getMacroData()} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={45} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                        {getMacroData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex justify-center gap-4 mt-2 text-xs">
                    {getMacroData().map((item, idx) => (
                      <div key={idx} className="flex items-center gap-1">
                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[idx] }}></div>
                        <span className="text-gray-500">{item.name}: {item.value}g</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            <div className="px-5 pt-4">
              <label className="block text-xs font-medium text-gray-500 mb-1">Filter by date</label>
              <DatePicker
                selected={selectedDate}
                onChange={(date) => setSelectedDate(date)}
                className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-orange-300"
                dateFormat="MMMM d, yyyy"
              />
            </div>

            <div className="p-5 space-y-3">
              {historyLoading ? (
                <div className="text-center py-8">
                  <div className="inline-block w-6 h-6 border-2 border-gray-200 border-t-orange-500 rounded-full animate-spin"></div>
                  <p className="text-sm text-gray-400 mt-2">Loading...</p>
                </div>
              ) : filteredMeals.length === 0 ? (
                <div className="text-center py-8">
                  <span className="text-4xl">🍽️</span>
                  <p className="text-sm text-gray-400 mt-2">No meals on {selectedDate.toLocaleDateString()}</p>
                </div>
              ) : (
                filteredMeals.map((meal) => (
                  <div key={meal.id} className="bg-gray-50 rounded-xl p-3 border border-gray-100">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xl">{getFoodEmoji(meal.food_name)}</span>
                          <span className="font-medium text-gray-800 capitalize">{meal.food_name}</span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          {new Date(meal.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                        <div className="flex flex-wrap gap-3 mt-2 text-xs">
                          <span className="text-red-500">🔥 {meal.nutrition.calories} cal</span>
                          <span className="text-blue-500">💪 {meal.nutrition.protein}g</span>
                          <span className="text-yellow-500">🍚 {meal.nutrition.carbs}g</span>
                          <span className="text-purple-500">🧈 {meal.nutrition.fat}g</span>
                          <span className="text-pink-500">🍬 {meal.nutrition.sugar}g</span>
                        </div>
                      </div>
                      <button
                        onClick={() => deleteMeal(meal.id)}
                        className="text-gray-400 hover:text-red-500 text-sm transition px-2"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 max-w-lg mx-auto w-full">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%]`}>
              <div className={`rounded-2xl px-4 py-2 ${msg.type === 'user' ? 'bg-gradient-to-r from-orange-500 to-orange-600 text-white' : 'bg-white shadow-md border border-gray-100'}`}>
                {msg.imagePreview && <img src={msg.imagePreview} alt="Uploaded" className="rounded-xl max-h-40 w-auto mb-2" />}
                {msg.component && <msg.component />}
                {!msg.component && !msg.numberInput && <p className="whitespace-pre-wrap text-sm">{msg.content}</p>}
                {msg.numberInput && (
                  <>
                    <p className="whitespace-pre-wrap text-sm mb-2">{msg.content}</p>
                    <NumberInputComponent question={msg.numberInput} onSubmit={handleNumberSubmit} />
                  </>
                )}
              </div>

              {msg.options && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {msg.options.map((opt, idx) => {
                    const isSelected = currentMultiSelections[opt.questionId]?.includes(opt.value);
                    return (
                      <button
                        key={idx}
                        onClick={() => {
                          if (opt.action === "new" || opt.action === "home") resetChat();
                          else if (opt.action === "retry") {
                            setPreview(null);
                            addMessage("bot", "Ready to try again!", [{ label: "📸 Take a photo", action: "camera" }, { label: "📁 Upload", action: "upload" }]);
                          } else if (opt.action === "camera" || opt.action === "upload") handleUserAction(opt.action);
                          else if (opt.value) handleAnswer(opt, opt.isMulti || false);
                        }}
                        className={`px-4 py-2 rounded-full text-sm transition ${isSelected ? 'bg-green-500 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}
                      >
                        {opt.label} {isSelected && '✓'}
                      </button>
                    );
                  })}
                  {msg.options[0]?.isMulti && <button onClick={handleMultiSelectNext} className="px-4 py-2 bg-blue-500 text-white rounded-full">Next →</button>}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white shadow-md rounded-2xl px-4 py-2">
              <div className="flex gap-1"><div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div><div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div><div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Save Meal Button */}
      {result && isLoggedIn && (
        <div className="sticky bottom-0 bg-white/90 backdrop-blur-lg border-t border-gray-100 p-3">
          <button onClick={saveCurrentMeal} disabled={isSaving} className="w-full py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-medium hover:shadow-lg transition disabled:opacity-50">
            {isSaving ? "Saving..." : "💾 Save This Meal to History"}
          </button>
        </div>
      )}

      {/* Hidden File Inputs */}
      <input type="file" onChange={handleFileChange} ref={fileUploadRef} className="hidden" accept="image/*" />
      <input type="file" accept="image/*" capture="environment" onChange={handleFileChange} ref={mobileCameraRef} className="hidden" />

      {/* Webcam Modal */}
      {showWebcam && (
        <div className="fixed inset-0 bg-black/90 flex flex-col items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-4 max-w-md w-full">
            <Webcam audio={false} ref={webcamRef} screenshotFormat="image/jpeg" className="rounded-xl w-full" />
            <div className="flex gap-3 mt-4">
              <button onClick={captureFromWebcam} className="flex-1 bg-gradient-to-r from-orange-500 to-orange-600 text-white py-3 rounded-xl font-medium">📸 Capture</button>
              <button onClick={() => setShowWebcam(false)} className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-xl font-medium">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;