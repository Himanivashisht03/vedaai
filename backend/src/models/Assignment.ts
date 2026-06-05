import mongoose, { Schema, Document } from 'mongoose';
import { IAssignment } from '../types';

export interface AssignmentDocument extends Omit<IAssignment, '_id'>, Document {}

const AssignmentSchema = new Schema<AssignmentDocument>({
  subject: { type: String, required: true },
  topic: { type: String, required: true },
  dueDate: { type: Date, required: true },
  gradeLevel: { type: String, required: true },
  questionTypes: { type: [String], required: true },
  difficulty: { type: String, required: true },
  numberOfQuestions: { type: Number, required: true },
  totalMarks: { type: Number, required: true },
  additionalInstructions: { type: String },
  filePath: { type: String },
  fileText: { type: String },
  status: { type: String, enum: ['queued', 'processing', 'complete', 'failed'], default: 'queued' },
  jobId: { type: String }
}, {
  timestamps: true
});

export const Assignment = mongoose.model<AssignmentDocument>('Assignment', AssignmentSchema);
