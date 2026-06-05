export interface IAssignment {
  _id?: string;
  subject: string;
  topic: string;
  dueDate: Date;
  gradeLevel: string;
  questionTypes: string[];
  difficulty: string;
  numberOfQuestions: number;
  totalMarks: number;
  additionalInstructions?: string;
  filePath?: string;
  fileText?: string;
  status: 'queued' | 'processing' | 'complete' | 'failed';
  jobId?: string;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface IQuestion {
  questionNumber: number;
  text: string;
  options?: string[];
  difficulty: 'Easy' | 'Moderate' | 'Hard';
  marks: number;
  type: string;
}

export interface ISection {
  sectionLabel: string;
  sectionTitle: string;
  instruction: string;
  marks: number;
  questions: IQuestion[];
}

export interface IGeneratedPaper {
  title: string;
  subject: string;
  grade: string;
  totalMarks: number;
  timeAllowed: string;
  sections: ISection[];
}

export interface IResult {
  _id?: string;
  assignmentId: string;
  generatedPaper: IGeneratedPaper;
  rawPrompt: string;
  createdAt?: Date;
}
