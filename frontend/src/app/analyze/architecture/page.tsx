'use client';
import { GridBackground } from '@/components/GridBackground'
import React from 'react'
import ArchitectureGraph from '@/components/Graph/ArchitectureGraph';

function Architecture() {

  return (
    <div className='h-screen  w-full relative"'>
      <GridBackground/>
        <h1 className="text-xl lg:text-3xl fixed z-20 top-10 left-10 font-bold text-center bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">
          <span className="relative bg-clip-text text-transparent bg-no-repeat bg-gradient-to-r from-purple-500 via-violet-500 to-pink-500 py-4">Architecture Map</span>
        </h1>
      <div className="relative z-10 h-full w-full">
        <ArchitectureGraph />
      </div>
    </div>
  )
}

export default Architecture