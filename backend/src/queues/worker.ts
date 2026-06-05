import { Worker, Job } from 'bullmq';
import { createRedisConnection, redis } from '../config/redis';
import { Assignment } from '../models/Assignment';
import { Result } from '../models/Result';
import { buildPrompt, generatePaper } from '../services/aiService';
import { connectDB } from '../config/db';
import dotenv from 'dotenv';
dotenv.config();

// Require db connection for independent worker process
connectDB();

const worker = new Worker('paper-generation', async (job: Job) => {
  const { assignmentId } = job.data;
  console.log(`Processing job for assignment: ${assignmentId}`);

  try {
    const assignment = await Assignment.findById(assignmentId);
    if (!assignment) throw new Error('Assignment not found');

    assignment.status = 'processing';
    await assignment.save();
    await redis.set(`job:${assignmentId}`, JSON.stringify({ status: 'processing', progress: 10 }), 'EX', 3600);

    // This block runs if socket is in the same process, but typically we publish to redis or broadcast via http
    // Since worker might be separate, let's use redis pub/sub or just rely on polling for simplicity if socket isn't directly reachable.
    // However, we can use socket.io-redis adapter. For simplicity without it, we'll hit an endpoint or assume it runs in same process for dev.
    
    // Instead of importing socket here (which creates a new instance), we can just set Redis. The main server can poll Redis or we don't strictly need to emit from worker if using Redis.
    // To emit via socket from worker properly, we would normally use socket.io-redis emitter.
    // For this assessment, let's just update Redis. The frontend can poll, OR we can make an HTTP call to the main server to trigger the emit.

    const prompt = buildPrompt(assignment.toObject() as any);
    
    await redis.set(`job:${assignmentId}`, JSON.stringify({ status: 'processing', progress: 50 }), 'EX', 3600);
    
    const paper = await generatePaper(prompt);
    
    await redis.set(`job:${assignmentId}`, JSON.stringify({ status: 'processing', progress: 80 }), 'EX', 3600);

    const result = new Result({
      assignmentId: assignment._id,
      generatedPaper: paper,
      rawPrompt: prompt
    });

    await result.save();
    
    assignment.status = 'complete';
    await assignment.save();

    await redis.set(`result:${assignmentId}`, JSON.stringify(paper), 'EX', 3600);
    await redis.set(`job:${assignmentId}`, JSON.stringify({ status: 'complete', progress: 100 }), 'EX', 3600);

    return paper;

  } catch (error) {
    console.error(`Job failed: ${error}`);
    const assignment = await Assignment.findById(assignmentId);
    if (assignment) {
      assignment.status = 'failed';
      await assignment.save();
      await redis.set(`job:${assignmentId}`, JSON.stringify({ status: 'failed', progress: 0 }), 'EX', 3600);
    }
    throw error;
  }
}, {
  connection: createRedisConnection()
});

worker.on('completed', job => {
  console.log(`${job.id} has completed!`);
});

worker.on('failed', (job, err) => {
  console.log(`${job?.id} has failed with ${err.message}`);
});
