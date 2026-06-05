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
