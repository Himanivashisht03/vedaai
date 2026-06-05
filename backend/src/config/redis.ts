import Redis from 'ioredis';
import dotenv from 'dotenv';
dotenv.config();

const redisOptions = {
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379'),
  maxRetriesPerRequest: null
};

export const redis = new Redis(redisOptions);
export const createRedisConnection = () => new Redis(redisOptions);
