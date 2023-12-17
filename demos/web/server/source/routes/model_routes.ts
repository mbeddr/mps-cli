import express from 'express';
import controller from '../controllers/model_controller';
const router = express.Router();

router.get('/solutions', controller.getSolutions);
router.get('/modelsOfSolution/:solutionId', controller.getModelsOfSolution);

export = router;