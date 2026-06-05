import { Queue } from 'bullmq';
import { createRedisConnection } from '../config/redis';

export const generationQueue = new Queue('paper-generation', {
  connection: createRedisConnection()
});
