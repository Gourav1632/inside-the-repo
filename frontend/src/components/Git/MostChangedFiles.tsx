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
    <div className="bg-neutral-900 rounded-xl py-6 shadow-lg w-full h-full max-w-2xl border border-neutral-700 text-white overflow-hidden">
    <div className='text-2xl font-semibold px-6   mb-4 text-nowrap text-purple-400 '>Most Changed Files</div>
      <ul className="custom-scrollbar px-6 space-y-2 overflow-auto h-full">
        {files.map((file, index) => (
          <li key={index} className="flex justify-between">
            <span className="text-wrap">{file.file}</span>
            <span className="text-neutral-400">{file.changes} changes</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
