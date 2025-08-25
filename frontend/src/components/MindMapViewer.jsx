import React from 'react';
import './MindMapViewer.css';

const MindMapNode = ({ node }) => {
  if (!node) return null;
  return (
    <div className="mindmap-node">
      <div className="node-content">{node.name}</div>
      {Array.isArray(node.children) && node.children.length > 0 && (
        <div className="node-children">
          {node.children.map((child, idx) => (
            <MindMapNode key={idx} node={child} />
          ))}
        </div>
      )}
    </div>
  );
};

const MindMapViewer = ({ data }) => {
  // Accept either { name, children } or { root: { name, children } }
  const root = data.root || data;
  return (
    <div className="mindmap-container">
      <MindMapNode node={root} />
    </div>
  );
};

export default MindMapViewer;
