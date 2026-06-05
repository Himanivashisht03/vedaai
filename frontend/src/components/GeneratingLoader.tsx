import React from 'react';
import { Loader2 } from 'lucide-react';

export default function GeneratingLoader({ progress, status }: { progress: number, status: string }) {
  return (
    <div className="max-w-xl mx-auto bg-white rounded-2xl p-8 shadow-sm border border-slate-200 text-center">
      <div className="mb-6 relative flex justify-center">
        <div className="w-24 h-24 rounded-full border-4 border-slate-100 flex items-center justify-center relative">
          <Loader2 className="w-10 h-10 text-blue-600 animate-spin absolute" />
          <span className="text-lg font-bold text-slate-700 relative z-10 bg-white px-2">{progress}%</span>
        </div>
      </div>
      
      <h3 className="text-xl font-bold text-slate-900 mb-2">
        {status === 'queued' ? 'Waiting in queue...' : 'Generating Assessment...'}
      </h3>
      <p className="text-slate-500 mb-8">
        Our AI is crafting high-quality questions based on your requirements.
        This usually takes about 10-20 seconds.
      </p>

      <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
        <div 
          className="bg-blue-600 h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}
