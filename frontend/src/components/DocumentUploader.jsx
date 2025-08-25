import React, { useState } from 'react';

const DocumentUploader = ({ onProcess, loading }) => {
  const [files, setFiles] = useState([]);
  const [youtubeUrl, setYoutubeUrl] = useState('');

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleUrlChange = (e) => {
    setYoutubeUrl(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onProcess(files, youtubeUrl);
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 16 }}>
      <div>
        <label>Upload files (pdf/doc/docx/txt): </label>
        <input type="file" multiple onChange={handleFileChange} />
      </div>
      <div style={{ marginTop: 8 }}>
        <label>YouTube URL: </label>
        <input
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          value={youtubeUrl}
          onChange={handleUrlChange}
          style={{ width: 360 }}
        />
      </div>
      <button type="submit" disabled={loading} style={{ marginTop: 8 }}>
        {loading ? 'Processing...' : 'Process'}
      </button>
    </form>
  );
};

export default DocumentUploader;
