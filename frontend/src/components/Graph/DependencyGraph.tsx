import React from 'react';
import { ReactFlow, Controls } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { getLayoutedGraph } from '@/components/Graph/Layout';
import { FileAnalysis } from '@/types/file_analysis_type';


function DependencyGraph({analysis}:{analysis:FileAnalysis}) {
    
    if (!analysis) return <div>Loading graph...</div>;
    console.log(analysis)

  const { nodes, edges } = getLayoutedGraph(
    analysis.file_graph.nodes,
    analysis.file_graph.edges,
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

export default DependencyGraph;
