'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useAssignmentStore } from '@/store/useAssignmentStore';
import api from '@/lib/api';
import QuestionPaper from '@/components/QuestionPaper';
import GeneratingLoader from '@/components/GeneratingLoader';
import PDFDownloadButton from '@/components/PDFDownloadButton';

export default function ResultPage() {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  
  const { 
    generationStatus, 
    generationProgress, 
    result,
    setStatus,
    setProgress,
    setResult
  } = useAssignmentStore();

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const fetchStatus = async () => {
      try {
        const { data } = await api.get(`/results/${id}`);
        if (data.status === 'complete' && data.result) {
          setStatus('complete');
          setResult(data.result);
          setLoading(false);
        } else {
          setStatus(data.status);
          setProgress(data.progress || 0);
          setLoading(false);
          // Poll every 2 seconds if still processing/queued
          if (data.status !== 'failed') {
            interval = setTimeout(fetchStatus, 2000);
          }
        }
      } catch (error) {
        console.error(error);
        setStatus('failed');
        setLoading(false);
      }
    };

    fetchStatus();

    return () => clearTimeout(interval);
  }, [id, setStatus, setProgress, setResult]);

  const handleRegenerate = async () => {
    try {
      setStatus('queued');
      setProgress(0);
      setResult(null as unknown as import('@/types').IGeneratedPaper);
      await api.post(`/assignments/${id}/regenerate`);
    } catch (error) {
      console.error(error);
    }
  };

  if (loading) return <div className="p-8 text-center">Loading...</div>;

  if (generationStatus === 'failed') {
    return (
      <div className="p-8 text-center bg-red-50 text-red-600 rounded-xl border border-red-200">
        <h2 className="text-xl font-bold mb-2">Generation Failed</h2>
        <p>Something went wrong while generating the assessment.</p>
        <button onClick={handleRegenerate} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
          Try Again
        </button>
      </div>
    );
  }

  if (generationStatus !== 'complete' || !result) {
    return <GeneratingLoader progress={generationProgress} status={generationStatus} />;
  }

  return (
    <div className="pb-24">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-slate-900">Generated Assessment</h2>
        <div className="flex gap-3">
          <button 
            onClick={handleRegenerate}
            className="px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg shadow-sm hover:bg-slate-50 transition font-medium"
          >
            Regenerate
          </button>
          <PDFDownloadButton result={result} />
        </div>
      </div>
      
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <QuestionPaper paper={result} />
      </div>
    </div>
  );
}
