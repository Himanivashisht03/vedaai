import mongoose, { Schema, Document } from 'mongoose';
import { IResult } from '../types';

export interface ResultDocument extends Omit<IResult, '_id'>, Document {}

const ResultSchema = new Schema<ResultDocument>({
  assignmentId: { type: Schema.Types.ObjectId, ref: 'Assignment', required: true, unique: true },
  generatedPaper: { type: Object, required: true },
  rawPrompt: { type: String, required: true }
}, {
  timestamps: true
});

export const Result = mongoose.model<ResultDocument>('Result', ResultSchema);
