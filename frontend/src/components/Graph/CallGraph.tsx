import React, { useEffect, useState } from 'react';
import { ReactFlow, Controls } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { getLayoutedGraph } from '@/components/Graph/Layout';


function CallGraph({analysis}) {
    
    if (!analysis) return <div>Loading graph...</div>;
    console.log(analysis)

  const { nodes, edges } = getLayoutedGraph(
    analysis.call_graph.nodes,
    analysis.call_graph.edges,
    'TB'
  );

  const proOptions = { hideAttribution: true };

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <ReactFlow
        defaultNodes={nodes}
        defaultEdges={edges}
        fitView
        proOptions={proOptions}
        nodesDraggable
      >
        <Controls />
      </ReactFlow>
    </div>
  );
}

export default CallGraph;
