import { Request, Response } from 'express';
import { validationResult } from 'express-validator';
import fs from 'fs';
import pdfParse from 'pdf-parse';
import { Assignment } from '../models/Assignment';
import { generationQueue } from '../queues/generationQueue';
import { redis } from '../config/redis';

export const createAssignment = async (req: Request, res: Response) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const data = req.body;
    let fileText = '';

    if (req.file) {
      if (req.file.mimetype === 'application/pdf') {
        const dataBuffer = fs.readFileSync(req.file.path);
        const parsed = await pdfParse(dataBuffer);
        fileText = parsed.text;
      } else {
        fileText = fs.readFileSync(req.file.path, 'utf8');
      }
    }

    const assignment = new Assignment({
      ...data,
      questionTypes: Array.isArray(data.questionTypes) ? data.questionTypes : JSON.parse(data.questionTypes || '[]'),
      filePath: req.file?.path,
      fileText,
      status: 'queued'
    });

    await assignment.save();

    const job = await generationQueue.add('generate', { assignmentId: assignment._id });
    
    assignment.jobId = job.id;
    await assignment.save();

    // Cache initial state
    await redis.set(`job:${assignment._id}`, JSON.stringify({ status: 'queued', progress: 0 }), 'EX', 3600);

    res.status(201).json({ assignmentId: assignment._id, status: 'queued' });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Server error' });
  }
};

export const getAssignment = async (req: Request, res: Response) => {
  try {
    const assignment = await Assignment.findById(req.params.id);
    if (!assignment) {
      return res.status(404).json({ error: 'Not found' });
    }
    res.json(assignment);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
};

export const regenerateAssignment = async (req: Request, res: Response) => {
  try {
    const assignment = await Assignment.findById(req.params.id);
    if (!assignment) return res.status(404).json({ error: 'Not found' });

    // delete old result
    const { Result } = await import('../models/Result');
    await Result.findOneAndDelete({ assignmentId: assignment._id });

    assignment.status = 'queued';
    const job = await generationQueue.add('generate', { assignmentId: assignment._id });
    assignment.jobId = job.id;
    await assignment.save();

    await redis.set(`job:${assignment._id}`, JSON.stringify({ status: 'queued', progress: 0 }), 'EX', 3600);

    res.json({ assignmentId: assignment._id, status: 'queued' });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
};
