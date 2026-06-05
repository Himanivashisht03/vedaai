import { Router } from 'express';
import { createAssignment, getAssignment, regenerateAssignment } from '../controllers/assignments.controller';
import { upload } from '../middleware/upload';

const router = Router();

router.post('/', upload.single('file'), createAssignment);
router.get('/:id', getAssignment);
router.post('/:id/regenerate', regenerateAssignment);

export default router;
