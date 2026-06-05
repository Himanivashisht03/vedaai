import { Request, Response } from 'express';
import { Result } from '../models/Result';
import { Assignment } from '../models/Assignment';
import { redis } from '../config/redis';

export const getResult = async (req: Request, res: Response) => {
  try {
    const assignmentId = req.params.assignmentId;
    
    const assignment = await Assignment.findById(assignmentId);
    if (!assignment) {
      return res.status(404).json({ error: 'Assignment not found' });
    }

    if (assignment.status === 'complete') {
      const cached = await redis.get(`result:${assignmentId}`);
      if (cached) {
        return res.json({ status: 'complete', result: JSON.parse(cached) });
      }

      const result = await Result.findOne({ assignmentId });
      if (result) {
        await redis.set(`result:${assignmentId}`, JSON.stringify(result.generatedPaper), 'EX', 3600);
        return res.json({ status: 'complete', result: result.generatedPaper });
      }
    }

    const cachedState = await redis.get(`job:${assignmentId}`);
    if (cachedState) {
      return res.json(JSON.parse(cachedState));
    }

    res.json({ status: assignment.status, progress: assignment.status === 'processing' ? 50 : 0 });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
};
