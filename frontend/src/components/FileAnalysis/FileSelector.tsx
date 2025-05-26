import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { fileAnalysisRoute } from '@/utils/APIRoutes';
import { Analysis } from '@/types/repo_analysis_type';
import { askAssistantRoute } from '@/utils/APIRoutes';

const FileSelector = ({
  selectedFile,
  onFileSelect,
}: {
  selectedFile: string;
  onFileSelect: () => void;
}) => {
  const [fileList, setFileList] = useState<string[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [currentSelectedFile, setCurrentSelectedFile] = useState(selectedFile);

  useEffect(() => {
    const storedData = localStorage.getItem('repoAnalysis');
    if (storedData) {
      setAnalysis(JSON.parse(storedData));
    }

    const files = localStorage.getItem('fileList');
    if (files) {
      setFileList(JSON.parse(files));
    }
  }, []);

  const handleFileClick = async (file: string) => {
    const storageKey = `fileAnalysis-${file}`;
    const cached = localStorage.getItem(storageKey);
    let response;

    setLoading(true); 

    if (!cached && analysis) {

      // Reset chat history id for current selected file
      const history_id = localStorage.getItem('history_id');
      if (history_id) {
        try{
          const response = await axios.post(askAssistantRoute, {
            reset: true,
            history_id,
            question: "",
            code: ""
          });
          console.log(response.data.message);
          localStorage.removeItem('history_id');
        }catch(e){
          console.log("Error resetting history id:",e)
        }
      }
      const file_ast = analysis.repo_analysis.ast[file];
      if (!file_ast) {
        console.warn(`AST not found for file: ${file}`);
        setLoading(false);
        return;
      }

    try {
        response = await axios.post(fileAnalysisRoute, {
          file_path: file,
          file_ast,
          repo_url: analysis.repo_url,
          branch: 'main',
        });
    } catch (e) {
            console.error(`Error fetching ${file} data: ${e}`);
            setLoading(false);
            return;
    }
        if (response?.data) {
        localStorage.setItem(storageKey, JSON.stringify(response.data));
    }
}
    localStorage.setItem('lastUsedFile', file);
    setCurrentSelectedFile(file);
    setLoading(false); 
    setIsOpen(false)
    onFileSelect()
  };

  return (
    <div className="relative z-50 font-semibold w-full max-w-[800px] text-left">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-[#121212] text-white text-xl lg:text-3xl px-4 py-2 rounded-xl"
        disabled={loading}
      >
        {loading ? 'Requesting file data...' : currentSelectedFile}
      </button>

      {isOpen && (
        <ul className="custom-scrollbar p-2 absolute mt-2 w-full max-h-60 overflow-auto bg-[#121212] shadow-lg border rounded-xl">
          {fileList.length > 0 ? (
            fileList.map((file) => (
              <li
                key={file}
                onClick={() => {
                  handleFileClick(file);
                }}
                className="px-4 py-2 break-all text-white hover:text-[#d24cc1] cursor-pointer"
              >
                {file}
              </li>
            ))
          ) : (
            <li className="px-4 py-2 text-white">No files found</li>
          )}
        </ul>
      )}
    </div>
  );
};

export default FileSelector;
