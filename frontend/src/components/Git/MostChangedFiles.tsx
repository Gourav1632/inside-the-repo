import React from 'react';

interface FileChange {
  file: string;
  changes: number;
}

interface MostChangedFilesProps {
  files: FileChange[];
}

export const MostChangedFiles: React.FC<MostChangedFilesProps> = ({ files }) => {
  return (
    <div className="bg-neutral-900 rounded-xl py-6 shadow-lg w-full h-full   border border-neutral-700 text-white overflow-hidden">
    <div className='text-2xl font-semibold px-6   mb-4  text-purple-400 text-wrap '>Most Changed Files (Recent 50 commits)</div>
      <ul className="custom-scrollbar px-6 space-y-2 max-h-56 overflow-auto h-full">
        {files.map((file, index) => (
          <li key={index} className="flex justify-between gap-2">
            <span className="break-all ">{file.file}</span>
            <span className="text-neutral-400 text-nowrap">{file.changes} changes</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
