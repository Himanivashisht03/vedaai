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
