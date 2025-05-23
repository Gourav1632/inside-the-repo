"use client";
import React,{useState} from "react";
import { useRouter } from "next/navigation";
import { Spotlight } from "@/components/ui/spotlight-new";
import { PlaceholdersAndVanishInput } from "@/components/ui/placeholders-and-vanish-input";
import axios from "axios";
import {repoAnalysisRoute } from "@/utils/APIRoutes";
import LoadingScreen from "@/components/LoadingScreen";

export default function Home() {
    const [repoUrl,setRepoUrl] = useState("");
    const [loading,setLoading] = useState(false);
    const router = useRouter();
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setRepoUrl(e.target.value)
    };
  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    try{
      const response = await axios.post(repoAnalysisRoute, {
        repo_url:repoUrl,
        branch:"main"
      });
      const analysisData = {"repo_url":repoUrl, branch:"main",...response.data};
      localStorage.setItem("repoAnalysis", JSON.stringify(analysisData));
      router.push("/analyze")
    }catch(error){
      console.error("API error:", error);
    }finally{
      setLoading(false);
    }
  };

  if(loading){
    return (
      <LoadingScreen/>
    )
  }

  return (
    <div className="h-screen w-full  justify-center items-center rounded-md flex md:items-center md:justify-center bg-black/[0.96] antialiased bg-grid-white/[0.02] relative overflow-hidden">
      <Spotlight />
      <div className="flex flex-col justify-center items-center gap-4 p-4 max-w-7xl  mx-auto relative z-10  w-full">
        <h1 className="text-5xl md:text-7xl font-bold text-center bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">
          Into the <span className="relative bg-clip-text text-transparent bg-no-repeat bg-gradient-to-r from-purple-500 via-violet-500 to-pink-500 py-4">repo</span>
        </h1>
        <p className="font-normal text-xl  text-neutral-300 max-w-2xl text-center mx-auto">
          A smarter way to explore codebases—because reading thousands of lines shouldn't feel like decoding ancient scripts.
        </p>
        <div className="w-100">
        <PlaceholdersAndVanishInput placeholders={["Search a Git repository","Enter a repo URL"]} onChange={handleChange} onSubmit={onSubmit} />
        </div>
      </div>
    </div>
  );
}
