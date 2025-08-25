import React, { useState } from 'react';
import axios from 'axios';

const QuestionAnswer = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question) return;
    setLoading(true);
    setAnswer('');
    try {
      const formData = new FormData();
      formData.append('question', question);
      const response = await axios.post('http://localhost:8000/ask-question', formData);
      setAnswer(response.data.answer);
    } catch (error) {
      setAnswer(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleAsk}>
        <input
          type="text"
          placeholder="Ask a question about your documents..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={{ width: 400 }}
        />
        <button type="submit" disabled={loading} style={{ marginLeft: 8 }}>
          {loading ? 'Asking...' : 'Ask'}
        </button>
      </form>
      <div style={{ marginTop: 12, whiteSpace: 'pre-wrap' }}>
        {answer}
      </div>
    </div>
  );
};

export default QuestionAnswer;
