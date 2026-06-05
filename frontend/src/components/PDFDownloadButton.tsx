'use client';
import React from 'react';
import { IGeneratedPaper } from '@/types';
import { Download } from 'lucide-react';

export default function PDFDownloadButton({}: { result: IGeneratedPaper }) {
  const handlePrint = () => {
    window.print();
  };

  return (
    <button 
      onClick={handlePrint}
      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg shadow-sm hover:bg-blue-700 transition font-medium"
    >
      <Download className="w-4 h-4" />
      Download PDF
    </button>
  );
}
