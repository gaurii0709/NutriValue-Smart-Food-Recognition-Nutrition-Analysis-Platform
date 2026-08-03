import React, { useState, useEffect } from 'react';
import { foodAPI } from '../services/api';

const QuestionsComponent = ({ foodName, onComplete, onBack }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [questions, setQuestions] = useState([]);
  const [baseNutrition, setBaseNutrition] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    loadQuestions();
  }, [foodName]);

  const loadQuestions = async () => {
    setLoading(true);
    const result = await foodAPI.getFoodQuestions(foodName);

    if (result.success) {
      setQuestions(result.data.questions);
      setBaseNutrition(result.data.base_nutrition);
    } else {
      setError(result.message || 'Failed to load questions');
    }
    setLoading(false);
  };

  const handleAnswer = (answer) => {
    const newAnswers = { ...answers, [currentIndex]: answer };
    setAnswers(newAnswers);

    // Move to next question or submit
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      // All questions answered - calculate nutrition
      calculateNutrition(newAnswers);
    }
  };

  const calculateNutrition = async (finalAnswers) => {
    setCalculating(true);
    const result = await foodAPI.calculateNutrition(foodName, finalAnswers);
    setCalculating(false);

    if (result.success) {
      onComplete(result.nutrition);
    } else {
      setError(result.error || 'Failed to calculate nutrition');
    }
  };

  const goBack = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    } else {
      onBack();
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading questions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>{error}</div>
        <button onClick={onBack} style={styles.button}>Go Back</button>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>No questions available for {foodName}</div>
        <button onClick={onBack} style={styles.button}>Go Back</button>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];

  return (
    <div style={styles.container}>
      {/* Progress bar */}
      <div style={styles.progressContainer}>
        <div style={styles.progressText}>
          Question {currentIndex + 1} of {questions.length}
        </div>
        <div style={styles.progressBar}>
          <div
            style={{
              ...styles.progressFill,
              width: `${((currentIndex + 1) / questions.length) * 100}%`
            }}
          />
        </div>
      </div>

      {/* Question card */}
      <div style={styles.questionCard}>
        <h2 style={styles.question}>{currentQuestion.question}</h2>

        <div style={styles.options}>
          {currentQuestion.options.map((option, idx) => (
            <button
              key={idx}
              onClick={() => handleAnswer(option)}
              style={styles.optionButton}
              disabled={calculating}
            >
              {option}
            </button>
          ))}
        </div>

        {/* Base nutrition preview */}
        {baseNutrition && currentIndex === 0 && (
          <div style={styles.basePreview}>
            <h4>Base Nutrition (per {baseNutrition.serving_size || 'serving'}):</h4>
            <div style={styles.nutritionGrid}>
              <span>🔥 {baseNutrition.calories} cal</span>
              <span>🥩 {baseNutrition.protein}g protein</span>
              <span>🍚 {baseNutrition.carbs}g carbs</span>
              <span>🧈 {baseNutrition.fat}g fat</span>
            </div>
            <p style={styles.note}>*Values will adjust based on your answers</p>
          </div>
        )}

        {/* Navigation buttons */}
        <div style={styles.navButtons}>
          <button onClick={goBack} style={styles.navButton}>
            ← Back
          </button>
        </div>
      </div>

      {calculating && (
        <div style={styles.calculating}>
          Calculating nutrition...
        </div>
      )}
    </div>
  );
};

// Styles
const styles = {
  container: {
    maxWidth: '600px',
    margin: '0 auto',
    padding: '20px',
  },
  progressContainer: {
    marginBottom: '20px',
  },
  progressText: {
    textAlign: 'center',
    marginBottom: '5px',
    color: '#666',
  },
  progressBar: {
    height: '8px',
    backgroundColor: '#e0e0e0',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4CAF50',
    transition: 'width 0.3s ease',
  },
  questionCard: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  },
  question: {
    fontSize: '20px',
    marginBottom: '20px',
    color: '#333',
  },
  options: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    marginBottom: '20px',
  },
  optionButton: {
    padding: '15px',
    fontSize: '16px',
    border: '2px solid #e0e0e0',
    borderRadius: '8px',
    backgroundColor: 'white',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    ':hover': {
      backgroundColor: '#4CAF50',
      color: 'white',
      borderColor: '#4CAF50',
    },
    ':disabled': {
      opacity: 0.5,
      cursor: 'not-allowed',
    },
  },
  basePreview: {
    marginTop: '20px',
    padding: '15px',
    backgroundColor: '#f5f5f5',
    borderRadius: '8px',
  },
  nutritionGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '10px',
    marginTop: '10px',
  },
  note: {
    fontSize: '12px',
    color: '#666',
    marginTop: '10px',
    fontStyle: 'italic',
  },
  navButtons: {
    display: 'flex',
    justifyContent: 'flex-start',
    marginTop: '20px',
  },
  navButton: {
    padding: '10px 20px',
    fontSize: '14px',
    border: 'none',
    borderRadius: '6px',
    backgroundColor: '#f0f0f0',
    cursor: 'pointer',
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    fontSize: '18px',
    color: '#666',
  },
  error: {
    textAlign: 'center',
    padding: '40px',
    fontSize: '18px',
    color: '#f44336',
  },
  calculating: {
    textAlign: 'center',
    marginTop: '20px',
    padding: '10px',
    backgroundColor: '#e3f2fd',
    borderRadius: '8px',
    color: '#1976d2',
  },
};

export default QuestionsComponent;