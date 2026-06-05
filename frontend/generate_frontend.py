import os

def write_file(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')

files = {
    "types/index.ts": """
export interface IGeneratedPaper {
  title: string;
  subject: string;
  grade: string;
  totalMarks: number;
  timeAllowed: string;
  sections: Array<{
    sectionLabel: string;
    sectionTitle: string;
    instruction: string;
    marks: number;
    questions: Array<{
      questionNumber: number;
      text: string;
      options?: string[];
      difficulty: 'Easy' | 'Moderate' | 'Hard';
      marks: number;
      type: string;
    }>;
  }>;
}
""",
    "store/useAssignmentStore.ts": """
import { create } from 'zustand';
import { IGeneratedPaper } from '../types';

interface AssignmentState {
  currentAssignment: any;
  generationStatus: 'idle' | 'queued' | 'processing' | 'complete' | 'failed';
  generationProgress: number;
  result: IGeneratedPaper | null;
  error: string | null;
  
  setAssignment: (data: any) => void;
  setStatus: (status: 'idle' | 'queued' | 'processing' | 'complete' | 'failed') => void;
  setProgress: (progress: number) => void;
  setResult: (result: IGeneratedPaper) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useAssignmentStore = create<AssignmentState>((set) => ({
  currentAssignment: null,
  generationStatus: 'idle',
  generationProgress: 0,
  result: null,
  error: null,
  
  setAssignment: (data) => set({ currentAssignment: data }),
  setStatus: (status) => set({ generationStatus: status }),
  setProgress: (progress) => set({ generationProgress: progress }),
  setResult: (result) => set({ result }),
  setError: (error) => set({ error }),
  reset: () => set({
    currentAssignment: null,
    generationStatus: 'idle',
    generationProgress: 0,
    result: null,
    error: null
  })
}));
""",
    "lib/api.ts": """
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
});

export default api;
""",
    "hooks/useSocket.ts": """
import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export const useSocket = (assignmentId: string | null) => {
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    if (!assignmentId) return;

    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);

    newSocket.emit('join', assignmentId);

    return () => {
      newSocket.close();
    };
  }, [assignmentId]);

  return socket;
};
""",
    "app/layout.tsx": """
import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'VedaAI - AI Assessment Creator',
  description: 'Generate high quality assessments using AI',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-50 text-slate-900 min-h-screen`}>
        <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
          <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">V</div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">VedaAI</h1>
            </div>
          </div>
        </header>
        <main className="max-w-5xl mx-auto px-4 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
""",
    "app/page.tsx": """
import { redirect } from 'next/navigation';

export default function Home() {
  redirect('/create');
}
""",
    "app/create/page.tsx": """
import AssignmentForm from '@/components/AssignmentForm';

export default function CreatePage() {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Create New Assessment</h1>
        <p className="text-slate-600">Fill in the details below to generate an AI-powered question paper.</p>
      </div>
      <AssignmentForm />
    </div>
  );
}
""",
    "app/result/[id]/page.tsx": """
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAssignmentStore } from '@/store/useAssignmentStore';
import api from '@/lib/api';
import QuestionPaper from '@/components/QuestionPaper';
import GeneratingLoader from '@/components/GeneratingLoader';
import PDFDownloadButton from '@/components/PDFDownloadButton';

export default function ResultPage() {
  const { id } = useParams();
  const router = useRouter();
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
      setResult(null as any);
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
""",
    "components/GeneratingLoader.tsx": """
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
""",
    "components/DifficultyBadge.tsx": """
import React from 'react';

export default function DifficultyBadge({ difficulty }: { difficulty: 'Easy' | 'Moderate' | 'Hard' }) {
  const colors = {
    Easy: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    Moderate: 'bg-amber-100 text-amber-700 border-amber-200',
    Hard: 'bg-red-100 text-red-700 border-red-200'
  };

  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${colors[difficulty] || colors.Moderate}`}>
      {difficulty}
    </span>
  );
}
""",
    "components/QuestionPaper.tsx": """
import React from 'react';
import { IGeneratedPaper } from '@/types';
import DifficultyBadge from './DifficultyBadge';

export default function QuestionPaper({ paper }: { paper: IGeneratedPaper }) {
  return (
    <div className="p-10 max-w-[800px] mx-auto bg-white" id="question-paper-content">
      {/* Header */}
      <div className="text-center border-b-2 border-slate-800 pb-6 mb-8">
        <h1 className="text-3xl font-serif font-bold text-slate-900 uppercase mb-2">{paper.title}</h1>
        <div className="grid grid-cols-3 gap-4 text-sm font-semibold text-slate-700 mt-6">
          <div className="text-left">Subject: {paper.subject}</div>
          <div className="text-center">Grade: {paper.grade}</div>
          <div className="text-right">Time: {paper.timeAllowed}</div>
        </div>
        <div className="text-right text-sm font-semibold text-slate-700 mt-1">
          Max Marks: {paper.totalMarks}
        </div>
      </div>

      {/* Student Info */}
      <div className="grid grid-cols-2 gap-x-12 gap-y-6 mb-12 text-sm">
        <div className="flex border-b border-slate-400 pb-1">
          <span className="font-semibold w-24">Name:</span>
        </div>
        <div className="flex border-b border-slate-400 pb-1">
          <span className="font-semibold w-24">Date:</span>
        </div>
        <div className="flex border-b border-slate-400 pb-1">
          <span className="font-semibold w-24">Roll No:</span>
        </div>
        <div className="flex border-b border-slate-400 pb-1">
          <span className="font-semibold w-24">Section:</span>
        </div>
      </div>

      {/* Sections */}
      <div className="space-y-12">
        {paper.sections.map((section, idx) => (
          <div key={idx} className="section-block">
            <div className="bg-slate-100 p-3 rounded-lg mb-6 flex justify-between items-center border border-slate-200">
              <div>
                <h3 className="font-bold text-lg text-slate-900">Section {section.sectionLabel}: {section.sectionTitle}</h3>
                <p className="text-slate-600 text-sm italic mt-1">{section.instruction}</p>
              </div>
              <div className="font-bold text-slate-700 whitespace-nowrap">
                [{section.marks} Marks]
              </div>
            </div>

            <div className="space-y-6 pl-2">
              {section.questions.map((q, qIdx) => (
                <div key={qIdx} className="flex gap-4">
                  <div className="font-bold text-slate-800 w-6 shrink-0">{q.questionNumber}.</div>
                  <div className="flex-1">
                    <div className="text-slate-800 leading-relaxed">{q.text}</div>
                    
                    {q.options && q.options.length > 0 && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3 pl-2">
                        {q.options.map((opt, optIdx) => (
                          <div key={optIdx} className="flex items-start gap-2 text-slate-700">
                            <span className="font-medium bg-slate-100 w-6 h-6 rounded-full flex items-center justify-center text-xs shrink-0 mt-0.5 border border-slate-200">
                              {String.fromCharCode(65 + optIdx)}
                            </span>
                            <span>{opt}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {/* Add blank space for subjective answers if needed, omitted for compactness */}
                  </div>
                  <div className="flex flex-col items-end gap-2 shrink-0">
                    <div className="font-semibold text-slate-700">[{q.marks}]</div>
                    <DifficultyBadge difficulty={q.difficulty} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-12 pt-6 border-t border-slate-300 text-center text-sm text-slate-500 italic">
        *** End of Question Paper ***
      </div>
    </div>
  );
}
""",
    "components/PDFDownloadButton.tsx": """
'use client';
import React from 'react';
import { IGeneratedPaper } from '@/types';
import { Download } from 'lucide-react';

export default function PDFDownloadButton({ result }: { result: IGeneratedPaper }) {
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
""",
    "components/AssignmentForm.tsx": """
'use client';

import React, { useState } from 'react';
import { useForm } from 'react-form';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { useAssignmentStore } from '@/store/useAssignmentStore';

const QUESTION_TYPES = [
  'Multiple Choice (MCQ)',
  'Short Answer',
  'Long Answer',
  'True/False',
  'Fill in the Blank'
];

export default function AssignmentForm() {
  const router = useRouter();
  const setStatus = useAssignmentStore(s => s.setStatus);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    
    const formData = new FormData(e.currentTarget);
    
    // Process checkboxes
    const types = Array.from(document.querySelectorAll('input[name="questionTypes"]:checked')).map(cb => (cb as HTMLInputElement).value);
    formData.delete('questionTypes');
    formData.append('questionTypes', JSON.stringify(types));

    if (file) {
      formData.append('file', file);
    }

    try {
      const { data } = await api.post('/assignments', formData);
      setStatus('queued');
      router.push(`/result/${data.assignmentId}`);
    } catch (error) {
      console.error(error);
      alert("Failed to create assignment.");
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-700">Subject *</label>
          <input required name="subject" type="text" className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" placeholder="e.g. Science" />
        </div>
        
        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-700">Topic *</label>
          <input required name="topic" type="text" className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" placeholder="e.g. Photosynthesis" />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-700">Due Date *</label>
          <input required name="dueDate" type="date" className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition" />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-700">Grade Level *</label>
          <select required name="gradeLevel" className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition bg-white">
            <option value="">Select Grade</option>
            {[6,7,8,9,10,11,12].map(g => <option key={g} value={`Grade ${g}`}>Grade {g}</option>)}
          </select>
        </div>

        <div className="space-y-2 md:col-span-2">
          <label className="text-sm font-semibold text-slate-700">Question Types *</label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {QUESTION_TYPES.map(qt => (
              <label key={qt} className="flex items-center gap-2 cursor-pointer p-3 border border-slate-200 rounded-lg hover:bg-slate-50 transition">
                <input type="checkbox" name="questionTypes" value={qt} className="w-4 h-4 text-blue-600 rounded" />
                <span className="text-sm text-slate-700">{qt}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-700">Difficulty *</label>
          <select required name="difficulty" className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition bg-white">
            <option value="">Select Difficulty</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
            <option value="Mixed">Mixed</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">No. of Questions *</label>
            <input required name="numberOfQuestions" type="number" min="1" max="50" className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700">Total Marks *</label>
            <input required name="totalMarks" type="number" min="1" className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition" />
          </div>
        </div>

        <div className="space-y-2 md:col-span-2">
          <label className="text-sm font-semibold text-slate-700">Context Material (Optional PDF/TXT)</label>
          <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center hover:bg-slate-50 transition cursor-pointer">
            <input 
              type="file" 
              accept=".pdf,.txt"
              className="hidden" 
              id="file-upload"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <span className="text-blue-600 font-semibold hover:underline">Click to upload</span> or drag and drop
              <p className="text-xs text-slate-500 mt-1">PDF or TXT up to 5MB</p>
              {file && <p className="text-sm text-emerald-600 mt-2 font-medium">Selected: {file.name}</p>}
            </label>
          </div>
        </div>

        <div className="space-y-2 md:col-span-2">
          <label className="text-sm font-semibold text-slate-700">Additional Instructions</label>
          <textarea name="additionalInstructions" rows={3} className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition resize-none" placeholder="Any specific requirements..."></textarea>
        </div>
      </div>

      <div className="mt-8 flex justify-end">
        <button 
          type="submit" 
          disabled={loading}
          className="px-8 py-3 bg-blue-600 text-white font-bold rounded-xl shadow-md hover:bg-blue-700 transition disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? 'Processing...' : 'Generate Assessment'}
        </button>
      </div>
    </form>
  );
}
"""
}

for path, content in files.items():
    write_file(path, content)
