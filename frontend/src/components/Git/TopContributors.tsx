import React from 'react';

interface Contributor {
  name: string;
  commits: number;
  avatar_url?: string;
}

interface TopContributorsProps {
  contributors: Contributor[];
}

export const TopContributors: React.FC<TopContributorsProps> = ({ contributors }) => {
  return (
    <div className="bg-neutral-900 py-6 rounded-xl shadow-lg w-full h-full  border border-neutral-700 text-white">
        <div className='text-2xl px-6 font-semibold mb-4 text-nowrap text-purple-400 '>Top Contributors</div>
        
      <ul className="space-y-2">
        {contributors.map((contributor, index) => (
          <li key={index} className="flex px-6 items-center max-h-56 space-x-4 overflow-auto h-full">
            <div>
              <p className="font-semibold">{contributor.name}</p>
              <p className="text-sm text-neutral-400">{contributor.commits} commits</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};
