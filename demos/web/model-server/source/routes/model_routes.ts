import express from 'express';
import controller from '../controllers/model_controller';
const router = express.Router();

router.get('/solutions', controller.getSolutions);
router.get('/modelsOfSolution/:solutionId', controller.getModelsOfSolution);
router.get('/rootNodesOfModel/:modelId', controller.getRootsOfModel);

export = router;