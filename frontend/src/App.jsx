import { useState } from 'react';
import axios from 'axios';
import DocumentUploader from './components/DocumentUploader.jsx';
import MindMapViewer from './components/MindMapViewer.jsx';
import QuizComponent from './components/QuizComponent.jsx';
import QuestionAnswer from './components/QuestionAnswer.jsx';
import './App.css';

function App() {
  const [activeView, setActiveView] = useState(null);
  const [mindMapData, setMindMapData] = useState(null);
  const [quizData, setQuizData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isProcessed, setIsProcessed] = useState(false);

  const handleProcessDocuments = async (files, youtubeUrl) => {
    setLoading(true);
    setIsProcessed(false);
    setMessage('Processing documents...');

    try {
      const formData = new FormData();
      if (files && files.length > 0) {
        files.forEach((file) => formData.append('files', file));
      }
      if (youtubeUrl) {
        formData.append('youtube_url', youtubeUrl);
      }

      await axios.post('http://127.0.0.1:8000/upload-docs', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setMessage('Documents processed successfully! You can now generate a mind map, quiz, or ask questions.');
      setIsProcessed(true);
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateMindMap = async () => {
    setLoading(true);
    setMessage('Generating mind map...');
    try {
      const response = await axios.get('http://127.0.0.1:8000/generate-mindmap');
      setMindMapData(response.data);
      // @ts-ignore
      setActiveView('mindmap');
      setMessage('Mind map generated successfully!');
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    setLoading(true);
    setMessage('Generating quiz...');
    try {
      const response = await axios.get(' http://127.0.0.1:8000/generate-quiz');
      setQuizData(response.data);
      // @ts-ignore
      setActiveView('quiz');
      setMessage('Quiz generated successfully!');
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAskQuestion = () => {
    // @ts-ignore
    setActiveView('qa');
  };

  const renderView = () => {
    switch (activeView) {
      // @ts-ignore
      case 'mindmap':
        return mindMapData ? <MindMapViewer data={mindMapData} /> : null;
      // @ts-ignore
      case 'quiz':
        return quizData ? <QuizComponent data={quizData} /> : null;
      // @ts-ignore
      case 'qa':
        return <QuestionAnswer />;
      default:
        return <div>Upload your documents or provide a YouTube link to get started.</div>;
    }
  };

  return (
    <div className="App">
      <h1>Doc → Mindmap / Quiz / Q&A</h1>

      <DocumentUploader onProcess={handleProcessDocuments} loading={loading} />

      <div style={{ marginTop: 16 }}>
        <button onClick={handleGenerateMindMap} disabled={!isProcessed || loading}>
          Generate Mind Map
        </button>
        <button onClick={handleGenerateQuiz} disabled={!isProcessed || loading} style={{ marginLeft: 8 }}>
          Generate Quiz
        </button>
        <button onClick={handleAskQuestion} disabled={!isProcessed || loading} style={{ marginLeft: 8 }}>
          Ask a Question
        </button>
      </div>

      <div style={{ marginTop: 16, minHeight: 24 }}>{loading ? 'Loading...' : message}</div>

      <div style={{ marginTop: 24 }}>{renderView()}</div>
    </div>
  );
}

export default App;
