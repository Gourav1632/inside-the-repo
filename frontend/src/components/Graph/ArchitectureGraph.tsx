'use client';

import React, { useEffect, useState } from 'react';
import { ReactFlow, Controls } from '@xyflow/react';
import type { Node as FlowNode } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { getLayoutedGraph } from '@/components/Graph/Layout';
import axios from 'axios';
import { askAssistantRoute, fileAnalysisRoute } from '@/utils/APIRoutes';
import { useRouter } from 'next/navigation';
import Loading from '../Loading';
import { motion, AnimatePresence } from 'framer-motion';

function ArchitectureGraph() {
  const [analysis, setAnalysis] = useState<any>(null);
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("Retrieving architecture map...");

  useEffect(() => {
    setLoading(true);
    const storedData = localStorage.getItem('repoAnalysis');
    if (!storedData) {
      setMessage("Architecture map not found. Please search for a repository.");
      return;
    }
    setAnalysis(JSON.parse(storedData));
    setLoading(false);
  }, []);

  const { nodes, edges } = analysis
    ? getLayoutedGraph(
        analysis.repo_analysis.dependency_graph.nodes,
        analysis.repo_analysis.dependency_graph.edges,
        'TB'
      )
    : { nodes: [], edges: [] };

  const proOptions = { hideAttribution: true };

  const getFileAST = (file_path: string) => {
    const astEntries = Object.entries(analysis.repo_analysis.ast);
    for (const [key, ast] of astEntries) {
      const pathWithoutExt = key.replace(/\.[^/.]+$/, '');
      if (pathWithoutExt === file_path) {
        return { file: key, file_ast: ast };
      }
    }
    return undefined;
  };

  const handleNodeClick = async (_: React.MouseEvent, node: FlowNode) => {
    setMessage("Requesting file data...");
    setLoading(true);
    try {
      const file_path = node.id;
      console.log("node clicked ", node.id);
      const result = getFileAST(file_path);

      if (!result) {
        console.warn(`AST not found for file: ${file_path}`);
        return;
      }

      const { file, file_ast } = result;
      localStorage.setItem("lastUsedFile", file);
      const storageKey = `fileAnalysis-${file}`;
      const cached = localStorage.getItem(storageKey);
      if (cached) {
        router.push(`/analyze/file-analysis`);
        return;
      }

      const history_id = localStorage.getItem('history_id');
      if (history_id) {
        const response = await axios.post(askAssistantRoute, {
          reset: true,
          history_id,
          question: "",
          code: ""
        });
        console.log(response.data.message);
        localStorage.removeItem('history_id');
      }

      const response = await axios.post(fileAnalysisRoute, {
        file_path: file,
        file_ast,
        repo_url: analysis.repo_url,
        branch: 'main',
      });

      localStorage.setItem(storageKey, JSON.stringify(response.data));
      router.push(`/analyze/file-analysis`);
    } catch (error) {
      console.log('Error fetching file:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Loading message={message} />
          </motion.div>
        ) : (
          <motion.div
            key="graph"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            style={{ height: '100%', width: '100%' }}
          >
            <ReactFlow
              defaultNodes={nodes}
              defaultEdges={edges}
              fitView
              proOptions={proOptions}
              onNodeClick={handleNodeClick}
              nodesDraggable
            >
              <Controls />
            </ReactFlow>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default ArchitectureGraph;
