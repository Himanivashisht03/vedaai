import { Router } from 'express';
import { getResult } from '../controllers/results.controller';

const router = Router();

router.get('/:assignmentId', getResult);

export default router;
