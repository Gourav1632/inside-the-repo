"use client";
import React, { useEffect, useState } from "react";
import { Spotlight } from "@/components/ui/spotlight-new";
import { Cover } from "@/components/ui/cover";
import { progressRoute } from "@/utils/APIRoutes";

export default function LoadingScreen({requestId}:{requestId:string}) {
    const [progressMessage, setProgressMessage] = useState("");

    useEffect(() => {
    const eventSource = new EventSource(`${progressRoute}?request_id=${requestId}`);

    eventSource.onmessage = (event) => {
      const progressMessage = event.data;
      setProgressMessage(progressMessage);
    };

    eventSource.addEventListener('done', () => {
      eventSource.close();
    });

    eventSource.onerror = () => {
      console.error('SSE connection error');
      eventSource.close();
    };

    return () => eventSource.close();
  }, [requestId]);


  const firstSpaceIndex = progressMessage.indexOf(" ");
  const firstWord = firstSpaceIndex === -1 ? progressMessage : progressMessage.slice(0, firstSpaceIndex);
  const restOfMessage = firstSpaceIndex === -1 ? "" : progressMessage.slice(firstSpaceIndex);



return (
  <div className="h-screen flex flex-col justify-center items-center bg-black/[0.96] antialiased bg-grid-white/[0.02] relative overflow-hidden px-4">
    <Spotlight />
    <h1 className="text-2xl px-4 md:text-3xl lg:text-3xl font-semibold max-w-7xl mx-auto text-center mt-6 relative z-20 py-6 bg-clip-text text-transparent bg-gradient-to-b from-neutral-800 via-neutral-700 to-neutral-700 dark:from-neutral-800 dark:via-white dark:to-white transition-opacity duration-500 ease-in-out">
      <Cover>{firstWord}</Cover> 
      <span style={{wordBreak: 'break-word'}}>{restOfMessage}</span>
    </h1>
  </div>
);
}