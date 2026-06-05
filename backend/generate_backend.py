import os

def write_file(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')

files = {
    "src/types/index.ts": """
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
""",
    "src/config/db.ts": """
import mongoose from 'mongoose';

export const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/vedaai');
    console.log(`MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error(`Error connecting to MongoDB: ${error}`);
    process.exit(1);
  }
};
""",
    "src/config/redis.ts": """
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
""",
    "src/config/socket.ts": """
import { Server } from 'socket.io';
import { Server as HttpServer } from 'http';

let io: Server;

export const initSocket = (server: HttpServer) => {
  io = new Server(server, {
    cors: {
      origin: '*', // Allow all origins for dev
      methods: ['GET', 'POST']
    }
  });

  io.on('connection', (socket) => {
    console.log(`Socket connected: ${socket.id}`);
    
    socket.on('join', (assignmentId) => {
      socket.join(`assignment:${assignmentId}`);
      console.log(`Socket ${socket.id} joined room assignment:${assignmentId}`);
    });

    socket.on('disconnect', () => {
      console.log(`Socket disconnected: ${socket.id}`);
    });
  });

  return io;
};

export const getIo = () => {
  if (!io) {
    throw new Error('Socket.io not initialized!');
  }
  return io;
};
""",
    "src/models/Assignment.ts": """
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
""",
    "src/models/Result.ts": """
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
""",
    "src/queues/generationQueue.ts": """
import { Queue } from 'bullmq';
import { createRedisConnection } from '../config/redis';

export const generationQueue = new Queue('paper-generation', {
  connection: createRedisConnection()
});
""",
    "src/middleware/upload.ts": """
import multer from 'multer';
import path from 'path';
import fs from 'fs';

const uploadDir = path.join(__dirname, '../../uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

export const upload = multer({ 
  storage: storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf' || file.mimetype === 'text/plain') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF or TXT files are allowed'));
    }
  }
});
""",
    "src/services/aiService.ts": """
import Anthropic from '@anthropic-ai/sdk';
import { IAssignment } from '../types';
import dotenv from 'dotenv';
dotenv.config();

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || 'dummy_key'
});

export const buildPrompt = (assignment: IAssignment): string => {
  return `
You are an expert curriculum designer and teacher. Create a question paper based on the following requirements:

Subject: ${assignment.subject}
Topic: ${assignment.topic}
Grade Level: ${assignment.gradeLevel}
Total Marks: ${assignment.totalMarks}
Number of Questions: ${assignment.numberOfQuestions}
Difficulty: ${assignment.difficulty}
Question Types: ${assignment.questionTypes.join(', ')}
Additional Instructions: ${assignment.additionalInstructions || 'None'}

Context Material from teacher (if any):
${assignment.fileText ? assignment.fileText : 'None'}

OUTPUT FORMAT:
You MUST return ONLY valid JSON matching this exact structure, with no markdown formatting or extra text outside the JSON:

{
  "title": "Topic Test: ${assignment.topic}",
  "subject": "${assignment.subject}",
  "grade": "${assignment.gradeLevel}",
  "totalMarks": ${assignment.totalMarks},
  "timeAllowed": "1 Hour",
  "sections": [
    {
      "sectionLabel": "A",
      "sectionTitle": "Multiple Choice Questions",
      "instruction": "Attempt all questions",
      "marks": 10,
      "questions": [
        {
          "questionNumber": 1,
          "text": "What is...?",
          "options": ["A", "B", "C", "D"], // Only if MCQ
          "difficulty": "Easy", // Must be "Easy", "Moderate", or "Hard"
          "marks": 2,
          "type": "MCQ"
        }
      ]
    }
  ]
}

Ensure the sum of marks of all questions equals ${assignment.totalMarks}.
Ensure the number of questions equals ${assignment.numberOfQuestions}.
The question difficulties should reflect the requested difficulty: ${assignment.difficulty}.
`;
};

export const generatePaper = async (prompt: string): Promise<any> => {
  // If no API key is provided, we can return a mock for testing without failing
  if (!process.env.ANTHROPIC_API_KEY) {
    console.log("WARNING: NO ANTHROPIC_API_KEY provided, returning mock data.");
    return {
      title: "Mock AI Generated Paper",
      subject: "Math",
      grade: "Grade 10",
      totalMarks: 10,
      timeAllowed: "1 Hour",
      sections: [
        {
          "sectionLabel": "A",
          "sectionTitle": "General Questions",
          "instruction": "Attempt all",
          "marks": 10,
          "questions": [
            {
              "questionNumber": 1,
              "text": "What is 2+2?",
              "options": ["3", "4", "5", "6"],
              "difficulty": "Easy",
              "marks": 10,
              "type": "MCQ"
            }
          ]
        }
      ]
    };
  }

  const msg = await anthropic.messages.create({
    model: 'claude-3-5-sonnet-20241022',
    max_tokens: 4000,
    temperature: 0.2,
    messages: [
      { role: 'user', content: prompt }
    ]
  });
  
  let responseText = msg.content[0].text;
  
  // Clean markdown if AI returned it
  if (responseText.includes('```json')) {
    responseText = responseText.split('```json')[1].split('```')[0].trim();
  } else if (responseText.includes('```')) {
    responseText = responseText.split('```')[1].split('```')[0].trim();
  }
  
  return JSON.parse(responseText);
};
""",
    "src/controllers/assignments.controller.ts": """
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
""",
    "src/controllers/results.controller.ts": """
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
""",
    "src/routes/assignments.ts": """
import { Router } from 'express';
import { createAssignment, getAssignment, regenerateAssignment } from '../controllers/assignments.controller';
import { upload } from '../middleware/upload';

const router = Router();

router.post('/', upload.single('file'), createAssignment);
router.get('/:id', getAssignment);
router.post('/:id/regenerate', regenerateAssignment);

export default router;
""",
    "src/routes/results.ts": """
import { Router } from 'express';
import { getResult } from '../controllers/results.controller';

const router = Router();

router.get('/:assignmentId', getResult);

export default router;
""",
    "src/index.ts": """
import express from 'express';
import http from 'http';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { connectDB } from './config/db';
import { initSocket } from './config/socket';
import assignmentsRouter from './routes/assignments';
import resultsRouter from './routes/results';

dotenv.config();

const app = express();
const server = http.createServer(app);

app.use(cors());
app.use(helmet());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

connectDB();
initSocket(server);

app.use('/api/assignments', assignmentsRouter);
app.use('/api/results', resultsRouter);

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
""",
    "src/queues/worker.ts": """
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
"""
}

for path, content in files.items():
    write_file(path, content)
