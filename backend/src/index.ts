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
