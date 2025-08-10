import React from "react";
import ReactFlow, { Background, Controls } from "reactflow";

export default function FlowRenderer({ mapJson }) {
  if (!mapJson) return <div>No map</div>;

  const nodes = (mapJson.nodes || []).map((n, i) => ({
    id: n.id || `n${i}`,
    type: "default",
    data: { label: <div><strong>{n.label}</strong><div style={{fontSize:12}}>{n.details}</div></div> },
    position: n.position || { x: Math.random() * 400, y: Math.random() * 300 },
  }));

  const edges = (mapJson.edges || []).map((e, i) => ({
    id: `e${i}`,
    source: e.from,
    target: e.to,
    label: e.label || "",
    animated: false,
    type: "smoothstep"
  }));

  return (
    <div style={{ width: "100%", height: "80vh" }}>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
