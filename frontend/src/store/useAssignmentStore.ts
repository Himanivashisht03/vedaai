import { create } from 'zustand';
import { IGeneratedPaper } from '../types';

interface AssignmentState {
  currentAssignment: Record<string, unknown> | null;
  generationStatus: 'idle' | 'queued' | 'processing' | 'complete' | 'failed';
  generationProgress: number;
  result: IGeneratedPaper | null;
  error: string | null;
  
  setAssignment: (data: Record<string, unknown>) => void;
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
