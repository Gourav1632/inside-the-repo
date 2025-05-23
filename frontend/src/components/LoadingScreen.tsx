"use client";
import React, { useEffect, useState } from "react";
import { Spotlight } from "@/components/ui/spotlight-new";
import { Cover } from "@/components/ui/cover";

export default function LoadingScreen() {
  const messages = [
    "Collecting source code.",
    "Analyzing code structure..",
    "Building the architecture map...",
    "Testing your patience....",
    "Putting the pieces together....."
  ];
  const message_length =  messages.length

  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    if (messageIndex < message_length - 1) {
      const timeout = setTimeout(() => {
        setMessageIndex((prev) => prev + 1);
      },3000); 
      return () => clearTimeout(timeout);
    }
  }, [messageIndex,message_length]);

  const currentMessage = messages[messageIndex];
  const firstSpaceIndex = currentMessage.indexOf(" ");
  const firstWord = firstSpaceIndex === -1 ? currentMessage : currentMessage.slice(0, firstSpaceIndex);
  const restOfMessage = firstSpaceIndex === -1 ? "" : currentMessage.slice(firstSpaceIndex);



  return (
    <div className="h-screen flex flex-col justify-center items-center bg-black/[0.96] antialiased bg-grid-white/[0.02] relative overflow-hidden">
      <Spotlight />
      <h1 className="text-2xl md:text-3xl lg:text-3xl font-semibold max-w-7xl mx-auto text-center mt-6 relative z-20 py-6 bg-clip-text text-transparent bg-gradient-to-b from-neutral-800 via-neutral-700 to-neutral-700 dark:from-neutral-800 dark:via-white dark:to-white transition-opacity duration-500 ease-in-out">
        <Cover>{firstWord}</Cover> {restOfMessage}
      </h1>
    </div>
  );
}
