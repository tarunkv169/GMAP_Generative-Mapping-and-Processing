import React, { useState } from "react";
import { uploadFile, uploadYoutube, generateMap } from "./api";
import FlowRenderer from "./FlowRenderer";

function App() {
  const [file, setFile] = useState(null);
  const [yt, setYt] = useState("");
  const [map, setMap] = useState(null);
  const [status, setStatus] = useState("");

  const onUploadFile = async () => {
    if (!file) return alert("Pick a file");
    setStatus("Uploading...");
    const r = await uploadFile(file);
    setStatus(r.message);
  };

  const onUploadYt = async () => {
    if (!yt) return;
    setStatus("Processing YouTube...");
    const r = await uploadYoutube(yt);
    setStatus(r.message);
  };

  const onGenerate = async () => {
    setStatus("Generating map...");
    const r = await generateMap("Create a concise concept map with nodes and edges from my uploaded content");
    setMap(r.map);
    setStatus("Map generated");
  };

  return (
    <div style={{ padding: 24 }}>
      <h1>RAG Map Creator (Gemini)</h1>
      <div>
        <input type="file" onChange={(e)=>setFile(
// @ts-ignore
        e.target.files[0])} />
        <button onClick={onUploadFile}>Upload</button>
      </div>
      <div style={{ marginTop: 8 }}>
        <input placeholder="YouTube URL" value={yt} onChange={e=>setYt(e.target.value)} />
        <button onClick={onUploadYt}>Add YouTube</button>
      </div>
      <div style={{ marginTop: 8 }}>
        <button onClick={onGenerate}>Generate Map</button>
      </div>
      <div>{status}</div>
      <div style={{ marginTop: 16 }}>
        <FlowRenderer mapJson={map} />
      </div>
    </div>
  );
}

export default App;
