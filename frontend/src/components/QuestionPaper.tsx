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
