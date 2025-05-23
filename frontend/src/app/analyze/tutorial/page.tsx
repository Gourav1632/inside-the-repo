'use client';
import { GridBackground } from '@/components/GridBackground';
import React, { useEffect, useState } from 'react';
import Loading from '@/components/Loading';
import FileTutorial from '@/components/Tutorial/FileTutorial';
import { FileCodeViewer } from '@/components/FileAnalysis/FileCodeViewer';
import { motion } from 'framer-motion';

function Tutorial() {
  const [fileAnalysis, setFileAnalysis] = useState<any>(null);
  const [currentFile, setCurrentFile] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('Retrieving file contents...');

  useEffect(() => {
    const file = localStorage.getItem('lastUsedFile');
    if (!file) {
      setMessage('No file selected. Please select a file from architecture map.');
      setLoading(false);
      return;
    }
    setCurrentFile(file);
    const storageKey = `fileAnalysis-${file}`;
    const stored = localStorage.getItem(storageKey);

    if (stored) {
      setFileAnalysis(JSON.parse(stored));
    }
    setLoading(false);
  }, []);

  const extractHighlightedLines = (): number[] => {
    const steps = fileAnalysis?.analysis?.tutorial ?? [];
    const allLines = new Set<number>();

    steps.forEach((step: any) => {
      if (Array.isArray(step.lines)) {
        step.lines.forEach((line: number | [number, number]) => {
          if (Array.isArray(line)) {
            const [start, end] = line;
            for (let i = start; i <= end; i++) {
              allLines.add(i);
            }
          } else {
            allLines.add(line);
          }
        });
      }
    });

    return Array.from(allLines).sort((a, b) => a - b);
  };

  if (loading) return <Loading message={message} />;

  const highlightLines = extractHighlightedLines();

  return (
    <div className="h-screen flex justify-center items-center w-full relative">
      <GridBackground />
      <h1 className="text-xl lg:text-3xl fixed z-20 top-10 left-10 font-bold text-center bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">
        <span className="relative bg-clip-text text-transparent bg-no-repeat bg-gradient-to-r from-purple-500 via-violet-500 to-pink-500 py-4">
          Tutorial
        </span>
        : {currentFile}
      </h1>

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="relative z-10 flex justify-center items-center gap-4 w-[80%] h-[70vh]"
      >
        {Array.isArray(fileAnalysis?.analysis?.tutorial) &&
        fileAnalysis.analysis.tutorial.length > 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: 'easeOut', delay: 0.1 }}
            className="z-10 w-full h-full flex justify-center items-center"
          >
            <FileTutorial steps={fileAnalysis.analysis.tutorial} />
          </motion.div>
        ) : (
          <div className="relative z-20 bg-gradient-to-b h-screen flex justify-center items-center from-neutral-200 to-neutral-500 bg-clip-text py-8 text-xl font-bold text-transparent">
            Could not generate tutorial.
          </div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut', delay: 0.2 }}
          className="max-w-xl h-full flex justify-center items-center w-full"
        >
          <FileCodeViewer
            language={fileAnalysis?.analysis.language}
            code={fileAnalysis?.analysis.code}
            highlightLines={highlightLines}
          />
        </motion.div>
      </motion.div>
    </div>
  );
}

export default Tutorial;
