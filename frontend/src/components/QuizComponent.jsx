import React, { useState } from 'react';

const QuizComponent = ({ data }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);

  if (!data || data.length === 0) {
    return <div>No quiz available.</div>;
  }

  const currentQuestion = data[currentQuestionIndex];

  const handleSubmit = () => {
    if (selectedAnswer == null) return;
    if (selectedAnswer === currentQuestion.correctAnswer) {
      setScore((s) => s + 1);
    }
    if (currentQuestionIndex + 1 < data.length) {
      setCurrentQuestionIndex((i) => i + 1);
      setSelectedAnswer(null);
    } else {
      setShowResult(true);
    }
  };

  if (showResult) {
    return (
      <div>
        <h3>Quiz Finished</h3>
        <div>
          Score: {score} / {data.length}
        </div>
      </div>
    );
  }

  return (
    <div>
      <h3>Question {currentQuestionIndex + 1} of {data.length}</h3>
      <div style={{ marginBottom: 8 }}>{currentQuestion.question}</div>
      <div>
        {currentQuestion.options.map((opt, idx) => (
          <label key={idx} style={{ display: 'block', marginBottom: 4 }}>
            <input
              type="radio"
              name="answer"
              value={opt}
              checked={selectedAnswer === opt}
              onChange={() => setSelectedAnswer(opt)}
            />
            {' '}
            {opt}
          </label>
        ))}
      </div>
      <button onClick={handleSubmit} style={{ marginTop: 8 }}>Next</button>
    </div>
  );
};

export default QuizComponent;
