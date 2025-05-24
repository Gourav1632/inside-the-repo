'use client';

import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { GridBackground } from '@/components/GridBackground';
import Loading from '@/components/Loading';
import { PlaceholdersAndVanishInput } from '@/components/ui/placeholders-and-vanish-input';
import { askAssistantRoute } from '@/utils/APIRoutes';
import clsx from 'clsx';
import {motion} from "framer-motion"
import { FileAnalysis } from '@/types/file_analysis_type';

function Assistant() {
  const [currentFile, setCurrentFile] = useState<string>('');
  const [code, setCode] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('Preparing your assistant...');
  const [chat, setChat] = useState<{ role: string; content: string}[]>([]);
  const [input, setInput] = useState('');
  const [historyID, setHistoryID] = useState<string | null>(null);
  const [isThinking, setIsThinking] = useState(false);
  const chatRef = useRef<HTMLDivElement | null>(null);

  // Load file info
useEffect(() => {
  const file = localStorage.getItem('lastUsedFile');
  const storedHistoryID = localStorage.getItem('history_id');

  if (storedHistoryID) {
    setHistoryID(storedHistoryID);
  }

  if (!file) {
    setMessage('No file selected. Please select a file from architecture map.');
    setLoading(false);
    return;
  }

  setCurrentFile(file);

  const stored = localStorage.getItem(`fileAnalysis-${file}`);
  if (stored) {
    const parsed: FileAnalysis = JSON.parse(stored);
    setCode(JSON.stringify(parsed.analysis.code)); 
  } else {
    setMessage('No analysis found for selected file.');
  }

  setLoading(false);
}, []); 


  // Scroll to bottom on new message
  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' });
  }, [chat]);

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setChat(prev => [...prev, userMessage]);
    setInput('');
    setIsThinking(true);

    try {
      const res = await axios.post(askAssistantRoute, {
        question: input,
        code: code,
        history_id: historyID,
        reset: false,
      });

      const data = res.data;



      if (!historyID && data.history_id) {
        localStorage.setItem('history_id',data.history_id)
        setHistoryID(data.history_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: data.answer || 'Sorry something went wrong. Please try again later.'
      };

      setChat(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.log(err)
      setChat(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, something went wrong. Please try again.',
        },
      ]);
    } finally {
      setIsThinking(false);
    }
  };

  if (loading) return <Loading message={message} />;

  return (
    <div className="w-full h-screen flex flex-col relative overflow-hidden">
      <GridBackground />

      {/* Heading */}
      <motion.h1
        className="relative text-xl w-full text-left p-10 lg:text-3xl z-20 font-bold bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <span className="relative bg-clip-text text-transparent bg-no-repeat bg-gradient-to-r from-purple-500 via-violet-500 to-pink-500 py-4">
          Assistant:
        </span> <span className='break-all'>{currentFile}</span>
      </motion.h1>

    <div className='flex flex-col justify-center items-center h-[80vh]'>
      {/* Chat History */}
      <div
        ref={chatRef}
        className="h-[70vh] rounded-xl  z-10 px-4 overflow-y-auto w-full max-w-3xl  mb-4 space-y-4 custom-scrollbar"
      >
        {chat.map((msg, index) => (
          <div
            key={index}
            className={clsx(
              'px-4 py-2 rounded-xl max-w-[80%] whitespace-pre-wrap break-words',
              msg.role === 'user'
                ? 'bg-no-repeat bg-gradient-to-r from-purple-500 via-violet-500 to-pink-500 text-white self-end ml-auto'
                : 'bg-neutral-200 text-black self-start'
            )}
          >
              {msg.content}
          </div>
        ))}

        {isThinking && (
          <div className="bg-neutral-200 text-black self-start px-4 py-2 rounded-xl max-w-[80%] animate-pulse">
            Thinking...
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-8  w-full   lg:max-w-3xl  z-20">
        <PlaceholdersAndVanishInput
          placeholders={[`Ask something about ${currentFile}`]}
          onChange={e => setInput(e.target.value)}
          onSubmit={handleSubmit}
        />
      </div>
    </div>
    </div>
  );
}

export default Assistant;
