'use client';

import React, { useState } from 'react';

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
